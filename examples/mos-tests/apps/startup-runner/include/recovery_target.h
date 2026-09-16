#pragma once
#include "recovery.h"
// Target adapter. Reuses the startup file/hash helpers and the qualified wire layer.
extern "C" { uint8_t recovery_diagnostic[64]={}; }
namespace recovery_target {
using namespace recovery;
static Slot slots[2];static unsigned chosen;static uint8_t allocation[24];
static char saved_script[8193],compare_text[16384],file_list[16384];
static uint32_t inspected_bytes=0,hashed_bytes=0,last_ended=0;static unsigned last_mask=0;
inline bool collect_receipts(bool allow_orphans=false);
inline bool accepted_parent(const uint8_t* id);
inline bool armed_valid();
inline bool child_metadata(const char* directory,uint8_t* parent,uint8_t* digest,unsigned mask,const uint8_t* script);
inline bool child_bundle(const char* receipt_path,uint8_t* digest,bool save);

static const char* const slot_paths[2]={"/mos-tests/recovery-a.bin","/mos-tests/recovery-b.bin"};
inline Slot& latest(){return slots[chosen];}
inline void diagnose(uint8_t code){
 recovery_diagnostic[0]=code;
 printf("INCOMPLETE: recovery gate stopped (reason %u, phase %u, case %lu). No test was authorized.\n",
  code,recovery_diagnostic[1],(unsigned long)wire::get32(recovery_diagnostic+4));
 unsigned failures=recovery_diagnostic[8];for(unsigned i=0;i<3;++i)if(failures&(1<<i))printf("FAILED: %s has a confirmed failure in retained evidence.\n",CASES[i].id);
}
inline bool load(){
 size_t n=0;
 if(!readfile(slot_paths[0],slots[0].b,256,n)||n!=256||
    !readfile(slot_paths[1],slots[1].b,256,n)||n!=256||!pair(slots[0],slots[1],chosen))return false;
 Slot& s=latest();recovery_diagnostic[1]=s.phase();memcpy(recovery_diagnostic+16,s.b+24,16);
 wire::put32(recovery_diagnostic+4,wire::get32(s.b+124));
 if(!readfile("/mos-tests/install.bin",allocation,24,n)||n!=24||memcmp(allocation+20,"MSTI",4)||
    wire::get32(allocation+16)!=wire::crc(allocation,16)||memcmp(allocation,s.b+8,8))return false;
 return true;
}
inline bool commit_slot(Slot next){ next.seal();unsigned destination=chosen^1,selected=0;
 if(!pair(latest(),next,selected)||selected!=1)return false;
 FIL f={};if(ffs_fopen(&f,slot_paths[destination],FA_WRITE))return false;
 uint8_t status=0,zero_byte=0,commit=0xa5;
 bool ok=!ffs_flseek(&f,252)&&recording_write(&f,reinterpret_cast<char*>(&zero_byte),1,&status)==1&&!status&&!ffs_fsync(&f);
 next.b[252]=0;
 if(ok)ok=!ffs_flseek(&f,0)&&recording_write(&f,reinterpret_cast<char*>(next.b),256,&status)==256&&!status&&!ffs_fsync(&f);
 if(ok)ok=!ffs_flseek(&f,252)&&recording_write(&f,reinterpret_cast<char*>(&commit),1,&status)==1&&!status&&!ffs_fsync(&f);
 bool closed=ffs_fclose(&f)==0;next.b[252]=0xa5;
 Slot check;size_t n=0;
 if(!ok||!closed||!readfile(slot_paths[destination],check.b,256,n)||n!=256||memcmp(next.b,check.b,256))return false;
 slots[destination]=next;chosen=destination;return true;
}
inline bool publish(uint8_t phase,uint32_t key,uint32_t sequence,uint32_t length){
 Slot next=latest();if(next.generation()==UINT64_MAX)return false;
 put64(next.b+16,next.generation()+1);next.b[120]=phase;wire::put32(next.b+124,key);
 wire::put32(next.b+128,sequence);put64(next.b+132,length);
 if(phase==ALLOCATING){
  memcpy(next.b+24,session.id,16);memcpy(next.b+40,session.parent,16);memset(next.b+56,0,32);
  if(has_parent())memcpy(next.b+148,session.disposition,32);
  else {next.b[121]=0;memset(next.b+148,0,32);}
  memcpy(next.b+88,session.script,32);put64(next.b+140,u64(session.id+8));
 }else if(phase==BETWEEN)memcpy(next.b+56,session.hashes+64,32);
 return commit_slot(next);
}

inline bool checked_hash(const char* pathname,uint8_t* digest,uint32_t maximum){
 FILINFO info={};if(ffs_stat(&info,pathname)||(info.fattrib&0x10)||info.fsize>maximum)return false;
 size_t n=strlen(pathname);if(n>=5&&!strcmp(pathname+n-5,".json")&&info.fsize>16384)return false;
 if(info.fsize>67108864UL-hashed_bytes)return false;hashed_bytes+=info.fsize;
 return hashfile(pathname,digest);
}
inline bool digest_match(const char* pathname,const uint8_t* expected){
 uint8_t observed[32];return checked_hash(pathname,observed,1048576UL)&&!memcmp(observed,expected,32);
}
inline bool bounded_hash(const char* pathname,uint8_t* digest){
 return checked_hash(pathname,digest,16384);
}
inline bool from_hex(const char* s,uint8_t* bytes,size_t n){
 if(strlen(s)!=n*2)return false;
 for(size_t i=0;i<n;++i){unsigned a=0,b=0;char x=s[i*2],y=s[i*2+1];
  if(x>='0'&&x<='9')a=x-'0';else if(x>='a'&&x<='f')a=x-'a'+10;else return false;
  if(y>='0'&&y<='9')b=y-'0';else if(y>='a'&&y<='f')b=y-'a'+10;else return false;
  bytes[i]=(a<<4)|b;
 }return true;
}
// Only canonical manifests produced by this same bundle are supported in W02.
// Exact template equality is stricter than accepting arbitrary equivalent JSON.
inline bool inspect_run(const char* directory,const uint8_t* id,bool& complete,uint32_t& seq,uint32_t& length){
 char pathname[160],source[160];uint8_t hashes[128],script_hash[32],base_bundle[32],parent[16]={},disposition[32]={};size_t n=0;Selection selection;
 snprintf(pathname,sizeof pathname,"%s/selection-script.txt",directory);
 if(!readfile(pathname,saved_script,8192,n)||!parse_script(saved_script,n,FUNCTIONS,selection))return false;
 Sha256 sh;sh.add(saved_script,n);sh.finish(script_hash);last_mask=selection.mask;
 if(!child_metadata(directory,parent,disposition,selection.mask,script_hash))return false;
 const char* names[3]={"bundle.json","catalogue.json","target.json"};unsigned offsets[3]={0,32,96};
 for(unsigned i=0;i<3;++i){
  snprintf(source,sizeof source,"/mos-tests/%s",names[i]);snprintf(pathname,sizeof pathname,"%s/%s",directory,names[i]);
  if(!bounded_hash(source,hashes+offsets[i]))return false;
  if(i==0){memcpy(base_bundle,hashes,32);if(!zero(parent,16)){char receipt[160];snprintf(receipt,sizeof receipt,"%s/disposition.json",directory);if(!child_bundle(receipt,hashes,false))return false;}}
  if(!digest_match(pathname,hashes+offsets[i]))return false;
 }
 if(memcmp(hashes+32,CATALOGUE_DIGEST,32))return false;
 snprintf(source,sizeof source,"/mos-tests/plan-%u.json",selection.mask);
 if(!readfile(source,compare_text,sizeof compare_text-1,n))return false;compare_text[n]=0;
 char marker[65],digest[65];memset(marker,'@',64);marker[64]=0;char* at=strstr(compare_text,marker);
 if(!at||strstr(at+64,marker))return false;hex(script_hash,32,digest);memcpy(at,digest,64);
 Sha256 plan;plan.add(compare_text,n);plan.finish(hashes+64);
 snprintf(pathname,sizeof pathname,"%s/plan.json",directory);if(!digest_match(pathname,hashes+64))return false;
 // The original bundle inventory is mandatory; inspect every artifact it names.
 uint8_t list_hash[32];if(!bounded_hash("/mos-tests/files.lst",list_hash))return false;
 snprintf(pathname,sizeof pathname,"%s/files.lst",directory);if(!digest_match(pathname,list_hash))return false;
 if(!readfile("/mos-tests/files.lst",file_list,sizeof file_list-1,n))return false;file_list[n]=0;
 Sha256 bundle_check;char piece[300],catalogue_hex[65];hex(hashes+32,32,catalogue_hex);
 int piece_size=snprintf(piece,sizeof piece,"{\n  \"schema\": 1,\n  \"catalogue_sha256\": \"%s\",\n  \"artifacts\": [",catalogue_hex);
 bundle_check.add(piece,piece_size);unsigned inventory_count=0;char previous[81]={};
 char* line=file_list;while(*line){
  char* end=strchr(line,'\n');if(!end)return false;*end=0;char* space=strchr(line,' ');if(!space)return false;*space++=0;
  if(!*line||strlen(line)>80||strchr(line,'/')||strchr(line,'\\')||strstr(line,".."))return false;
  uint8_t expected[32];if(!from_hex(space,expected,32))return false;
  if(++inventory_count>120||strcmp(previous,line)>=0)return false;
  for(char* c=line;*c;++c)if(!((*c>='a'&&*c<='z')||(*c>='A'&&*c<='Z')||(*c>='0'&&*c<='9')||*c=='.'||*c=='_'||*c=='-'))return false;
  strcpy(previous,line);
  snprintf(pathname,sizeof pathname,"%s/%s",directory,line);FILINFO file_info={};
  if(ffs_stat(&file_info,pathname)||!digest_match(pathname,expected))return false;
  piece_size=snprintf(piece,sizeof piece,"%s\n    {\n      \"path\": \"%s\",\n      \"size\": %lu,\n      \"sha256\": \"%s\"\n    }",inventory_count==1?"":",",line,(unsigned long)file_info.fsize,space);
  if(piece_size<0||size_t(piece_size)>=sizeof piece)return false;bundle_check.add(piece,piece_size);line=end+1;
 }
 char list_hex[65];hex(list_hash,32,list_hex);
 piece_size=snprintf(piece,sizeof piece,",\n    {\n      \"path\": \"files.lst\",\n      \"size\": %lu,\n      \"sha256\": \"%s\"\n    }\n  ]\n}\n",(unsigned long)n,list_hex);
 bundle_check.add(piece,piece_size);uint8_t canonical_bundle[32];bundle_check.finish(canonical_bundle);
 if(!inventory_count||memcmp(canonical_bundle,base_bundle,32))return false;
 int size=render_manifest(compare_text,sizeof compare_text,id,parent,disposition,hashes);
 if(size<0||size_t(size)>=sizeof compare_text)return false;Sha256 manifest;uint8_t expected_run[32];manifest.add(compare_text,size);manifest.finish(expected_run);
 snprintf(pathname,sizeof pathname,"%s/run.json",directory);if(!digest_match(pathname,expected_run))return false;
 // Reject unexplained directory entries, including orphan disposition material.
 DIR dir={};FILINFO entry={};if(ffs_dopen(&dir,directory))return false;bool entries_ok=true;unsigned entries=0;
 while(entries_ok){if(ffs_dread(&dir,&entry)){entries_ok=false;break;}if(!entry.fname[0])break;
  if(++entries>128||(entry.fattrib&0x10)){entries_ok=false;break;}
  bool known=!zero(parent,16)&&!strcmp(entry.fname,"disposition.json");const char* extras[]={"bundle.json","run.json","plan.json","selection-script.txt","results.bin","files.lst"};
  for(auto name:extras)if(!strcmp(entry.fname,name))known=true;
  // Inventory was split into nul-terminated name/hash pairs above.
  char* cursor=file_list;while(cursor<file_list+n){
   char* hash=cursor+strlen(cursor)+1;if(!strcmp(cursor,entry.fname))known=true;cursor=hash+strlen(hash)+1;
  }
  if(!known)entries_ok=false;
 }
 bool dirclosed=ffs_dclose(&dir)==0;if(!entries_ok||!dirclosed)return false;
 snprintf(pathname,sizeof pathname,"%s/results.bin",directory);FIL f={};if(ffs_fopen(&f,pathname,FA_READ))return false;
 uint32_t total=0;bool ok=!ffs_fsize(&f,&total)&&total<=1048576UL&&inspected_bytes<=67108864UL-total;inspected_bytes+=ok?total:0;
 Records records(id,hashes,CASE_HASHES,selection.mask);uint8_t envelope[1069];
 while(ok&&records.bytes<total){
  if(total-records.bytes<40||ffs_fread(&f,reinterpret_cast<char*>(envelope),40)!=40){ok=false;break;}
  uint32_t payload=wire::get32(envelope+32);
  if(payload<2||payload>1024||total-records.bytes<45+payload||
     ffs_fread(&f,reinterpret_cast<char*>(envelope+40),payload+5)!=payload+5||
     (envelope[5]==1&&envelope[42]!=BACKEND)||!records.accept(envelope,payload+45)){ok=false;break;}
 }
 ok=!ffs_ferror(&f)&&ok;bool fileclosed=ffs_fclose(&f)==0;complete=ok&&fileclosed&&records.complete;seq=records.sequence;length=records.bytes;
 if(!memcmp(id,latest().b+24,16)){
  recovery_diagnostic[8]=records.failed_mask;wire::put32(recovery_diagnostic+4,records.current);
  if(memcmp(hashes+64,latest().b+56,32)||(latest().phase()<DISPOSING&&memcmp(script_hash,latest().b+88,32))||
     latest().sequence()>seq||latest().length()>length)ok=false;
 }
 last_ended=records.ended_mask;return ok&&fileclosed;
}
inline bool gate(){
 memset(recovery_diagnostic,0,64);recovery_diagnostic[1]=255;inspected_bytes=0;hashed_bytes=0;
 if(!load()){diagnose(1);return false;}
 Slot& s=latest();
 if(!collect_receipts()){diagnose(7);return false;}
 uint64_t count=u64(allocation+8);if(count>=4096||s.generation()==UINT64_MAX){diagnose(8);return false;}
 if(s.counter()!=count){diagnose(3);return false;}
 // Verify names/count once; deterministic paths below establish no missing counter.
 DIR d={};FILINFO e={};if(ffs_dopen(&d,"/mos-tests/runs")){diagnose(6);return false;}
 unsigned found=0;bool okay=true;
 while(okay){if(ffs_dread(&d,&e)){okay=false;break;}if(!e.fname[0])break;uint8_t id[16];
  if(++found>4096||!(e.fattrib&0x10)||!from_hex(e.fname,id,16)||memcmp(id,allocation,8)||!u64(id+8)||u64(id+8)>count)okay=false;
 }
 bool closed=ffs_dclose(&d)==0;if(!okay||!closed||found!=count){diagnose(3);return false;}
 for(uint64_t i=1;i<=count;++i){uint8_t id[16];memcpy(id,allocation,8);put64(id+8,i);char text[33],directory[80];hex(id,16,text);snprintf(directory,sizeof directory,"/mos-tests/runs/%s",text);
  bool complete=false;uint32_t seq=0,length=0;
  if(!inspect_run(directory,id,complete,seq,length)){diagnose(4);return false;}
  if(!complete&&!accepted_parent(id)){diagnose(5);return false;}
  if(i==count&&(s.sequence()!=seq||s.length()!=length)){diagnose(5);return false;}
 }
 if((count==0&&s.phase()!=IDLE)||(count>0&&s.phase()!=COMPLETE&&!(s.phase()==ARMED&&armed_valid()))){diagnose(2);return false;}
 recovery_diagnostic[0]=0;return true;
}
inline bool same_boot(){
 if(!load())return false;
 Slot& s=latest();
 return s.phase()==BETWEEN&&!memcmp(s.b+40,session.parent,16)&&!memcmp(s.b+148,session.disposition,32)&&
 !memcmp(s.b+24,session.id,16)&&!memcmp(s.b+56,session.hashes+64,32)&&
 !memcmp(s.b+88,session.script,32)&&s.length()==session.length&&s.counter()==u64(allocation+8);
}
inline bool position(RecordedLifecycle& bridge,uint8_t phase,uint32_t key){
 uint32_t size=0;MosStorage* storage=static_cast<MosStorage*>(bridge.recorder.io.context);
 return !ffs_fsize(&storage->file,&size)&&publish(phase,key,bridge.recorder.confirmed,size);
}
inline bool case_start(void* data,const Case& c){
 auto& b=*static_cast<RecordedLifecycle*>(data);
 return position(b,CASE_INTENT,c.key)&&RecordedLifecycle::start(data,c)&&position(b,IN_CASE,c.key);
}
inline bool case_finish(void* data,const Case& c,const Result& result){
 return RecordedLifecycle::finish(data,c,result)&&position(*static_cast<RecordedLifecycle*>(data),CASE_DONE,c.key);
}
}
