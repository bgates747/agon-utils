#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
namespace suite {
namespace wire {
inline void put16(uint8_t* p,uint16_t n) {p[0]=n;p[1]=n>>8;}
inline void put32(uint8_t* p,uint32_t n) {for(unsigned i=0;i<4;++i) p[i]=n>>(8*i);}
inline uint32_t get32(const uint8_t* p) {uint32_t n=0;for(unsigned i=0;i<4;++i)n|=uint32_t(p[i])<<(8*i);return n;}
inline uint32_t crc(const uint8_t* p,size_t n) {
 uint32_t c=UINT32_C(0xffffffff);while(n--) {c^=*p++;for(unsigned i=0;i<8;++i)c=(c>>1)^((c&1)?UINT32_C(0xedb88320):0);}return c^UINT32_C(0xffffffff);
}
// Typed constructors leave reserved bytes zero; strings are validated UTF-8.
inline bool utf8(const char* s,size_t n) {
 for(size_t i=0;i<n;) {uint8_t a=uint8_t(s[i++]);if(a<128)continue;
 unsigned k=a>=0xc2&&a<=0xdf?1:a>=0xe0&&a<=0xef?2:a>=0xf0&&a<=0xf4?3:0;
 if(!k||n-i<k)return false;uint8_t b=uint8_t(s[i]);
 if((a==0xe0&&b<0xa0)||(a==0xed&&b>=0xa0)||(a==0xf0&&b<0x90)||(a==0xf4&&b>=0x90))return false;
 while(k--)if((uint8_t(s[i++])&0xc0)!=0x80)return false;
 }return true;
}
struct Payload {
 uint8_t bytes[1024];uint16_t size;
 Payload():bytes{},size(0){}
 void init(uint16_t n) {memset(bytes,0,sizeof bytes);size=n;put16(bytes,1);}
 bool run_start(uint8_t backend,uint32_t count,const uint8_t* hashes) {if(backend<1||backend>2||!count)return false;init(136);bytes[2]=backend;put32(bytes+4,count);memcpy(bytes+8,hashes,128);return true;}
 bool case_start(uint16_t samples,const uint8_t* hashes) {if(!samples)return false;init(68);put16(bytes+2,samples);memcpy(bytes+4,hashes,64);return true;}
 bool observation(uint8_t kind,uint16_t sample,uint16_t chunk,uint16_t chunks,uint32_t id,const uint8_t* data,uint16_t n) {
  if(kind<1||kind>3||!chunks||chunk>=chunks||!id||n>1008||(kind==1&&(n!=96||chunk||chunks!=1)))return false;
  init(16+n);bytes[2]=kind;put16(bytes+4,sample);put16(bytes+6,chunk);put16(bytes+8,chunks);put16(bytes+10,n);put32(bytes+12,id);if(n)memcpy(bytes+16,data,n);return true;
 }
 bool case_end(uint8_t outcome,uint32_t assertions,uint32_t failed,uint32_t observations,const char* reason) {
  size_t n=strlen(reason);if(n>1004||!utf8(reason,n)||outcome<1||outcome>8||failed>assertions)return false;
  if(outcome==1&&(!assertions||failed||n))return false;
  if(outcome!=1&&!n)return false;if(outcome==2&&!failed)return false;
  if(outcome>=3&&outcome<=6&&(assertions||failed||(outcome>=4&&observations)))return false;
  init(20+n);bytes[2]=outcome;put32(bytes+4,assertions);put32(bytes+8,failed);put32(bytes+12,observations);put16(bytes+16,n);memcpy(bytes+20,reason,n);return true;
 }
 void error(uint8_t op,uint32_t status,uint32_t attempted,uint32_t confirmed) {init(16);bytes[2]=op;put32(bytes+4,status);put32(bytes+8,attempted);put32(bytes+12,confirmed);}
 void run_end(const uint32_t* counts,const uint8_t* plan) {init(68);for(unsigned i=0;i<8;++i)put32(bytes+4+4*i,counts[i]);memcpy(bytes+36,plan,32);}
};
inline uint16_t encode(uint8_t* out,uint8_t type,const uint8_t* run,uint32_t seq,uint32_t key,const Payload& p) {
 if(type<1||type>6||p.size<2||p.size>1024||!seq)return 0;
 memset(out,0,40);memcpy(out,"MSTR",4);out[4]=1;out[5]=type;put16(out+6,40);memcpy(out+8,run,16);put32(out+24,seq);put32(out+28,key);put32(out+32,p.size);memcpy(out+40,p.bytes,p.size);put32(out+40+p.size,crc(out,40+p.size));out[44+p.size]=0xa5;return 45+p.size;
}
}
struct Storage {
 void* context;
 size_t (*write)(void*,const uint8_t*,size_t,uint32_t* status);
 uint32_t (*sync)(void*);
 uint32_t (*close)(void*);
};
// Observer is a fault-injection seam after each individual SRAM byte store.
// Production uses nullptr. Interruption must never be caught and resumed in place.
struct Recorder {
 volatile uint8_t* ram;Storage io;uint8_t run_id[16],catalogue[32],plan[32];
 uint32_t next=1,confirmed=0,generation=0,current=0;uint16_t used=0;uint8_t state=1,slot=1;bool stopped=false;
 void (*stored)(void*,size_t)=nullptr;void* observer=nullptr;
 Recorder(volatile uint8_t* r,Storage s,const uint8_t* id,const uint8_t* cat,const uint8_t* pl):ram(r),io(s) {memcpy(run_id,id,16);memcpy(catalogue,cat,32);memcpy(plan,pl,32);}
 void store(size_t at,uint8_t value) {ram[at]=value;if(stored)stored(observer,at);}
 void publish_bytes(size_t at,const uint8_t* src,size_t n,size_t commit) {
  store(at+commit,0);for(size_t i=0;i<n;++i)if(i!=commit)store(at+i,src[i]);store(at+commit,0xa5);
 }
 bool publish() {
  if(generation==UINT32_MAX) {stopped=true;return false;}
  uint8_t b[128]={};memcpy(b,"MSTC",4);wire::put16(b+4,1);wire::put16(b+6,128);memcpy(b+8,run_id,16);
  wire::put32(b+24,++generation);wire::put32(b+28,next);wire::put32(b+32,confirmed);wire::put16(b+36,used);b[38]=state;
  wire::put32(b+40,current);memcpy(b+44,catalogue,32);memcpy(b+76,plan,32);wire::put32(b+120,wire::crc(b,120));b[124]=0xa5;
  slot^=1;publish_bytes(slot*128,b,128,124);return true;
 }
 bool begin() {
  uint8_t any=0;for(unsigned i=0;i<16;++i)any|=run_id[i];
  if(!any||!io.write||!io.sync||!io.close){stopped=true;return false;}
  // New run only, after collision-safe allocation; never recover by calling begin.
  store(124,0);store(252,0);for(size_t i=0xd00;i<0xe00;++i)store(i,0);
  return publish();
 }
 bool fail(uint8_t op,uint32_t status,uint32_t attempted) {
  if(stopped||state==6)return false;stopped=true;state=5;
  wire::Payload p;p.error(op,status,attempted,confirmed);uint8_t b[1069];
  // next is always reserved and nonzero: append refuses to consume UINT32_MAX.
  uint16_t n=wire::encode(b,5,run_id,next,current,p);publish_bytes(0xd00,b,n,n-1);publish();return false;
 }
 bool append(uint8_t type,const wire::Payload& p) {
  if(stopped||state==6)return false;
  if(next==UINT32_MAX)return fail(5,2,next);
  // Reserve enough generations for I/O confirmation and fatal publication.
  if(generation>UINT32_MAX-8)return fail(5,3,next);
  uint8_t b[1069];uint16_t n=wire::encode(b,type,run_id,next,current,p);
  if(!n)return fail(5,4,next);
  if(n>2048-used)return fail(4,0,next);
  publish_bytes(0x100+used,b,n,n-1);used+=n;++next;
  if(type==3)state=3;return publish();
 }
 bool checkpoint() {
  if(stopped||state==6)return false;if(!used)return true;
  state=4;if(!publish())return fail(5,3,next);
  // Volatile SRAM copied into normal RAM for the MOS ABI, outside capture window.
  uint8_t bytes[2048];for(uint16_t i=0;i<used;++i)bytes[i]=ram[0x100+i];
  uint32_t status=0;size_t wrote=io.write(io.context,bytes,used,&status);
  if(status||wrote!=used)return fail(1,status?status:UINT32_C(0xffffffff),next-1);
  status=io.sync(io.context);if(status)return fail(2,status,next-1);
  confirmed=next-1;used=0;state=current?2:1;
  // Both surviving slots must release the extent before any staging reuse.
  if(!publish()||!publish())return fail(5,3,next);
  return true;
 }
 bool start_case(uint32_t key,const wire::Payload& p) {
  if(stopped||state==6||current||!key)return false;current=key;state=2;return append(2,p)&&checkpoint();
 }
 bool finish_case(const wire::Payload& p) {
  if(stopped||!current)return false;
  if(!append(4,p)||!checkpoint())return false;current=0;state=1;return publish();
 }
 bool finish_run(const wire::Payload& p) {
  if(stopped||state==6||current)return false;if(!append(6,p)||!checkpoint())return false;
  uint32_t status=io.close(io.context);if(status)return fail(3,status,next-1);
  state=6;return publish();
 }
};
}
