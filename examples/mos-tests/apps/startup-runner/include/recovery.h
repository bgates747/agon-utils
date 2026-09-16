#pragma once
#include "recording.h"
namespace recovery {
using namespace suite;
inline uint16_t u16(const uint8_t* p){return p[0]|uint16_t(p[1])<<8;}
inline uint64_t u64(const uint8_t* p){uint64_t n=0;for(unsigned i=0;i<8;++i)n|=uint64_t(p[i])<<(8*i);return n;}
inline void put64(uint8_t* p,uint64_t n){for(unsigned i=0;i<8;++i)p[i]=n>>(8*i);}
inline bool zero(const uint8_t* p,size_t n){while(n--)if(*p++)return false;return true;}
enum Phase:uint8_t {IDLE,ALLOCATING,BETWEEN,CASE_INTENT,IN_CASE,CASE_DONE,FINALIZING,COMPLETE,DISPOSING,PARKED,ARMED};
struct Slot {
 uint8_t b[256]={};
 uint64_t generation()const{return u64(b+16);}
 uint64_t counter()const{return u64(b+140);}
 uint8_t phase()const{return b[120];}
 uint32_t sequence()const{return wire::get32(b+128);}
 uint64_t length()const{return u64(b+132);}
 void seal(){wire::put32(b+248,wire::crc(b,248));b[252]=0xa5;}
 bool valid()const{
  if(memcmp(b,"MSTJ",4)||u16(b+4)!=1||u16(b+6)!=256||!generation()||b[252]!=0xa5||
     wire::get32(b+248)!=wire::crc(b,248)||!zero(b+122,2)||!zero(b+180,68)||!zero(b+253,3)||
     phase()>ARMED||b[121]>3)return false;
  if(phase()==IDLE)return zero(b+24,224);
  if(zero(b+24,16)||memcmp(b+8,b+24,8)||u64(b+32)!=counter()||!counter()||zero(b+88,32))return false;
  if(phase()<DISPOSING){
   if(b[121]==0){if(!zero(b+40,16)||!zero(b+148,32))return false;}
   else if((b[121]!=2&&b[121]!=3)||zero(b+40,16)||zero(b+148,32)||memcmp(b+40,b+8,8)||u64(b+48)>=counter())return false;
   uint32_t key=wire::get32(b+124);
   if(phase()>=CASE_INTENT&&phase()<=CASE_DONE){if(key<1||key>3)return false;}
   else if(key)return false;
   if(phase()==ALLOCATING)return !sequence()&&!length()&&zero(b+56,32);
   if(!sequence()||!length()||zero(b+56,32))return false;
  }
  return true;
 }
};
// Reader accepts W01 wire states, while the W02 executor rejects dispositions.
inline bool edge(uint8_t a,uint8_t b){
 // A table avoids an AgonDev LLVM i9 legalization crash on the boolean chain.
 static const uint16_t allowed[11]={3,260,328,272,288,260,384,2,1792,256,258};
 if(a>ARMED||b>ARMED)return false;
 return (uint32_t(allowed[a])&(uint32_t(1)<<b))!=0;
}

inline bool pair(const Slot& a,const Slot& b,unsigned& selected){
 if(!a.valid()||!b.valid()||memcmp(a.b+8,b.b+8,8))return false;
 if(a.generation()==b.generation()){selected=0;return !memcmp(a.b,b.b,256);}
 selected=a.generation()>b.generation()?0:1;
 const Slot& old=selected? a:b;const Slot& now=selected?b:a;
 if(now.generation()-old.generation()!=1||!edge(old.phase(),now.phase()))return false;
 if(now.phase()==ALLOCATING){
  return old.counter()!=UINT64_MAX&&now.counter()==old.counter()+1&&
   !now.sequence()&&!now.length()&&zero(now.b+56,32)&&!wire::get32(now.b+124);
 }
 if(memcmp(old.b+24,now.b+24,16)||old.counter()!=now.counter())return false;
 if(now.sequence()<old.sequence()||now.length()<old.length())return false;
 if(old.phase()!=ALLOCATING&&now.phase()!=DISPOSING&&old.phase()!=DISPOSING&&
    memcmp(old.b+56,now.b+56,64))return false;
 return true;
}
// Streaming, deliberately restricted to the three qualified startup controls.
// More general record kinds remain a conservative unsupported-input error.
struct Records {
 uint8_t id[16],hashes[128],contracts[3][64];unsigned mask;
 uint32_t sequence=0,bytes=0,current=0,ended_mask=0,counts[8]={},observations=0;
 uint32_t failed_mask=0;bool begun=false,complete=false,difference=false;
 Records(const uint8_t* run,const uint8_t* h,const uint8_t c[3][64],unsigned m):mask(m){
  memcpy(id,run,16);memcpy(hashes,h,128);memcpy(contracts,c,192);
 }
 bool accept(const uint8_t* b,size_t n){
  if(n<47||n>1069||complete||memcmp(b,"MSTR",4)||b[4]!=1||u16(b+6)!=40||
   memcmp(b+8,id,16)||wire::get32(b+24)!=sequence+1||!zero(b+36,4)||
   wire::get32(b+32)+45!=n||b[n-1]!=0xa5||wire::get32(b+n-5)!=wire::crc(b,n-5))return false;
  const uint8_t* p=b+40;size_t len=n-45;uint32_t key=wire::get32(b+28);uint8_t type=b[5];
  if(u16(p)!=1)return false;
  if(type==1){
   if(begun||sequence||key||len!=136||p[3]||p[2]<1||p[2]>2||
      wire::get32(p+4)!=unsigned((mask&1)!=0)+unsigned((mask&2)!=0)+unsigned((mask&4)!=0)||
      memcmp(p+8,hashes,128))return false;
   begun=true;
  }else{
   if(!begun)return false;
   if(type==6){
    if(current||ended_mask!=mask||key||len!=68||!zero(p+2,2)||memcmp(p+36,hashes+64,32))return false;
    for(unsigned i=0;i<8;++i)if(wire::get32(p+4+4*i)!=counts[i])return false;
    complete=true;
   }else{
    if(key<1||key>3||!(mask&(1<<(key-1))))return false;
    if(type==2){
     unsigned next=1;while(next<=3&&(!(mask&(1<<(next-1)))||(ended_mask&(1<<(next-1)))))++next;
     if(current||key!=next||len!=68||u16(p+2)!=2||memcmp(p+4,contracts[key-1],64))return false;
     current=key;observations=0;difference=false;
    }else if(type==3){
     if(current!=key||key==3||observations>=2||len!=112||p[2]!=1||p[3]||
        u16(p+4)!=observations||u16(p+6)||u16(p+8)!=1||u16(p+10)!=96||wire::get32(p+12)!=1)return false;
     const uint8_t* before=p+16;const uint8_t* after=p+48;const uint8_t* preservation=p+80;
     for(unsigned i=0;i<32;++i){
      uint8_t expected=i<20?255:0;if(key==2&&i==13)expected=0x7f;
      if(preservation[i]!=expected)return false;
     }
     for(unsigned s=0;s<2;++s){const uint8_t* snap=s?after:before;
      if(u16(snap+26)!=0x3ff||!zero(snap+28,4)||snap[24]!=1||snap[25])return false;
     }
     for(unsigned i=0;i<26;++i)if((before[i]^after[i])&preservation[i])difference=true;
     ++observations;
    }else if(type==4){
     if(current!=key||len<20||p[3]||u16(p+18)||u16(p+16)!=len-20||wire::get32(p+12)!=observations)return false;
     uint8_t outcome=p[2];uint32_t assertions=wire::get32(p+4),failed=wire::get32(p+8);
     if(failed>assertions||memchr(p+20,0,len-20))return false;
     char reason[1005];if(len-20>1004)return false;memcpy(reason,p+20,len-20);reason[len-20]=0;
     if(!wire::utf8(reason,len-20))return false;
     if(key==3){if(outcome!=5||assertions||failed||observations||len==20)return false;}
     else if(observations!=2||((outcome!=1)&&(outcome!=2))||!assertions||
      (outcome==1&&(failed||difference||len!=20))||(outcome==2&&(!failed||len==20)))return false;
     ++counts[outcome-1];if(outcome==2)failed_mask|=1<<(key-1);ended_mask|=1<<(key-1);current=0;
    }else return false;
   }
  }
  ++sequence;bytes+=n;return true;
 }
};
}
