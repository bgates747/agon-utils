#include "recorded_lifecycle.h"
#include <assert.h>
#include <stdio.h>
#include <vector>
#include <string>
#include <fstream>
#include <iterator>
using namespace suite;
struct Disk {std::vector<uint8_t> bytes;int writes=0,syncs=0,closes=0,short_at=0,write_at=0,sync_at=0;bool close_fail=false;
 static size_t write(void* v,const uint8_t* p,size_t n,uint32_t* status){auto& d=*static_cast<Disk*>(v);++d.writes;if(d.writes==d.write_at){*status=9;return 0;}if(d.writes==d.short_at)--n;d.bytes.insert(d.bytes.end(),p,p+n);return n;}
 static uint32_t sync(void* v){auto& d=*static_cast<Disk*>(v);return ++d.syncs==d.sync_at?7:0;}
 static uint32_t close(void* v){auto& d=*static_cast<Disk*>(v);++d.closes;return d.close_fail?8:0;}
 Storage io(){return {this,write,sync,close};}
};
uint8_t id[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15},cat[32],plan[32];
std::vector<uint8_t> read(const std::string& path){std::ifstream f(path,std::ios::binary);assert(f);return {std::istreambuf_iterator<char>(f),{}};}
void save(const std::string& path,const uint8_t* p,size_t n){std::ofstream f(path,std::ios::binary);f.write(reinterpret_cast<const char*>(p),n);assert(f);}
struct Fixture {uint8_t ram[8192];Disk disk;Recorder r;Fixture():r(ram,disk.io(),id,cat,plan){memset(ram,0xc7,sizeof ram);assert(r.begin());}};
struct Context {RecordedLifecycle* bridge;int executions=0;};
bool metadata(void*,const Case&,wire::Payload& p){uint8_t h[64]={};return p.case_start(1,h);}
Result execute(void* v,const Case&){auto& c=*static_cast<Context*>(v);++c.executions;assert(c.bridge->recorder.confirmed==c.bridge->recorder.next-1&&c.bridge->recorder.used==0);uint8_t b[96]={};wire::Payload p;assert(p.observation(1,0,0,1,1,b,96));if(!c.bridge->observation(p))return {Outcome::Error,0,0,"checkpoint failed"};return {Outcome::Passed,1,0,""};}
bool cleanup(void*,const Case&){return true;}
Totals exercise(Fixture& f,Context& c) {RecordedLifecycle bridge(f.r,&c,metadata,execute,cleanup);c.bridge=&bridge;Case a{1,"a","f","g",0},b{2,"b","f","g",0};const Case* list[]={&a,&b};return run(list,2,0,bridge.hooks());}
// Independent slot validity uses a different byte-at-a-time CRC formulation.
uint32_t oracle_crc(const uint8_t* p,size_t n){uint32_t c=~uint32_t(0);for(size_t i=0;i<n;++i){uint8_t b=p[i];for(unsigned j=0;j<8;++j){bool bit=(c^b)&1;c>>=1;if(bit)c^=0xedb88320u;b>>=1;}}return ~c;}
bool slot_valid(const uint8_t* p){return !memcmp(p,"MSTC",4)&&p[124]==0xa5&&oracle_crc(p,120)==wire::get32(p+120);}
struct Cut {size_t remaining;};
void cut(void* p,size_t){if(--static_cast<Cut*>(p)->remaining==0)throw 1;}
int main(int argc,char** argv){assert(argc==3);std::string fixtures=argv[1],out=argv[2];memset(cat,0x22,32);memset(plan,0x33,32);
 assert(wire::crc(reinterpret_cast<const uint8_t*>("123456789"),9)==0xcbf43926u);
 const char* names[]={"run-start","case-start","observation","case-end","checkpoint-error","run-end"};
 for(const char* name:names){auto golden=read(fixtures+"/"+name+".bin");wire::Payload p;p.size=wire::get32(&golden[32]);memcpy(p.bytes,&golden[40],p.size);uint8_t encoded[1069];auto n=wire::encode(encoded,golden[5],id,wire::get32(&golden[24]),wire::get32(&golden[28]),p);assert(n==golden.size()&&!memcmp(encoded,golden.data(),n));save(out+"/"+name+".bin",encoded,n);}
 {Fixture f;auto g=read(fixtures+"/control-slot.bin");assert(!memcmp(g.data(),f.ram,128));}
 {wire::Payload p;uint8_t hashes[128];memset(hashes,0x11,32);memset(hashes+32,0x22,32);memset(hashes+64,0x33,32);memset(hashes+96,0x44,32);assert(p.run_start(1,1,hashes));auto g=read(fixtures+"/run-start.bin");assert(!memcmp(p.bytes,g.data()+40,136));memset(hashes,0x55,32);memset(hashes+32,0x66,32);assert(p.case_start(1,hashes));g=read(fixtures+"/case-start.bin");assert(!memcmp(p.bytes,g.data()+40,68));assert(p.case_end(1,1,0,1,""));g=read(fixtures+"/case-end.bin");assert(!memcmp(p.bytes,g.data()+40,20));uint32_t counts[8]={1};p.run_end(counts,plan);g=read(fixtures+"/run-end.bin");assert(!memcmp(p.bytes,g.data()+40,68));p.error(2,1,4,3);g=read(fixtures+"/checkpoint-error.bin");assert(!memcmp(p.bytes,g.data()+40,16));g=read(fixtures+"/observation.bin");assert(p.observation(1,0,0,1,1,g.data()+56,96));assert(!memcmp(p.bytes,g.data()+40,112));}
 {wire::Payload p;uint8_t b[1009]={};assert(p.observation(2,0,0,1,1,b,1008)&&p.size==1024);assert(!p.observation(2,0,0,1,1,b,1009));assert(!p.observation(1,0,0,1,1,b,95));assert(!p.case_end(1,0,0,0,""));assert(!p.case_end(2,1,0,0,"bad"));assert(!p.case_end(4,0,0,1,"skip"));assert(!p.case_end(7,0,0,0,"\xc0\x80"));p.size=0;uint8_t dst[1069];assert(!wire::encode(dst,1,id,1,0,p));}
 {Fixture f;Context c{};auto t=exercise(f,c);assert(t.complete&&t.terminal==2&&c.executions==2&&f.r.confirmed==6&&f.r.used==0);wire::Payload p;p.run_end(t.counts,plan);assert(f.r.finish_run(p));assert(f.disk.closes==1&&f.r.state==6);assert(!f.r.append(6,p)&&!f.r.finish_run(p));}
 // Failure at every start/observation/end checkpoint of two cases.
 unsigned failures=0;
 for(int mode=0;mode<3;++mode)for(int at=1;at<=6;++at){Fixture f;if(mode==0)f.disk.short_at=at;if(mode==1)f.disk.write_at=at;if(mode==2)f.disk.sync_at=at;Context c{};auto t=exercise(f,c);assert(!t.complete&&t.infrastructure_error&&f.r.stopped);assert(c.executions==(at+1)/3);assert(f.r.confirmed==uint32_t(at-1));assert(f.ram[0xd3c]==0xa5&&f.ram[0xd05]==5);int writes=f.disk.writes;assert(!f.r.checkpoint());wire::Payload p;p.init(2);assert(!f.r.append(3,p)&&writes==f.disk.writes);save(out+"/failure-"+std::to_string(mode)+"-"+std::to_string(at)+".sram",f.ram,8192);++failures;}
 {Fixture f;Context c{};auto t=exercise(f,c);wire::Payload p;p.run_end(t.counts,plan);f.disk.close_fail=true;assert(!f.r.finish_run(p)&&f.r.stopped&&f.ram[0xd2a]==3);++failures;}
 {Fixture f;wire::Payload p;uint8_t b[1008]={};assert(p.observation(2,0,0,1,1,b,1008));assert(f.r.append(3,p));std::vector<uint8_t> before(f.ram+0x100,f.ram+0x100+1069);assert(!f.r.append(3,p)&&f.r.stopped&&f.ram[0xd2a]==4);assert(!memcmp(before.data(),f.ram+0x100,before.size()));assert(f.disk.writes==0);++failures;}
 for(int mode=0;mode<2;++mode){Fixture f;wire::Payload p;p.init(2);if(!mode)f.r.next=UINT32_MAX;else f.r.generation=UINT32_MAX-7;assert(!f.r.append(3,p)&&f.r.stopped);++failures;}
 {Fixture f;wire::Payload p;uint8_t b[1008]={};assert(p.observation(2,0,0,1,1,b,1008));assert(f.r.append(3,p));assert(p.observation(2,0,0,1,2,b,918));assert(f.r.append(3,p)&&f.r.used==2048);assert(f.r.checkpoint()&&f.disk.bytes.size()==2048);}
 {uint8_t ram[8192];memset(ram,0xc7,sizeof ram);uint8_t zero[16]={};Disk d;Recorder r(ram,d.io(),zero,cat,plan);assert(!r.begin()&&r.stopped);for(auto byte:ram)assert(byte==0xc7);}
 // Exhaust every byte-store interruption in staged append, checkpoint publication,
 // and reuse. Independently validate at least one surviving slot and its extent.
 size_t cuts=0;
 for(int phase=0;phase<3;++phase){size_t completed=0;for(size_t n=1;n<2000;++n){Fixture f;wire::Payload p;uint8_t h[64]={};p.case_start(1,h);if(phase>0)assert(f.r.append(2,p));if(phase>1)assert(f.r.checkpoint());Cut stop{n};f.r.stored=cut;f.r.observer=&stop;bool interrupted=false;try {if(phase==1)f.r.checkpoint();else f.r.append(2,p);}catch(int){interrupted=true;}if(!interrupted){completed=n;break;}++cuts;
  bool any=false;for(unsigned s=0;s<2;++s){const uint8_t* b=f.ram+s*128;if(!slot_valid(b))continue;any=true;unsigned used=b[36]|unsigned(b[37])<<8;assert(used<=2048);if(used){assert(used==113);const uint8_t* rec=f.ram+256;assert(rec[112]==0xa5&&oracle_crc(rec,108)==wire::get32(rec+108));}}
  assert(any);
 }assert(completed);}
 // Interrupt emergency record publication at every store: valid only when complete.
 size_t emergency_cuts=0;
 for(size_t n=1;n<500;++n){Fixture f;wire::Payload p;p.init(2);assert(f.r.append(3,p));Cut stop{n};f.r.stored=cut;f.r.observer=&stop;bool interrupted=false;
  try {f.r.fail(2,7,1);}catch(int){interrupted=true;}
  if(!interrupted)break;++emergency_cuts;
  assert(slot_valid(f.ram)||slot_valid(f.ram+128));
  if(f.ram[0xd3c]==0xa5)assert(oracle_crc(f.ram+0xd00,56)==wire::get32(f.ram+0xd38));
  assert(f.disk.writes==0);
 }
 printf("PASSED: %zu interrupted emergency publications.\n",emergency_cuts);
 printf("PASSED: six frozen records and control slot; typed payloads/bounds; %u failure controls; %zu interrupted SRAM publications.\n",failures,cuts);
}
