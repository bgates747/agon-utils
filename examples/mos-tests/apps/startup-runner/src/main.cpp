#include "generated.h"
#include "sha256.h"
#include "script.h"
#include "continuation.h"
#include "capture.h"
#include "recorded_lifecycle.h"
#include "mos_storage.h"
#include <stdio.h>
#include <stdlib.h>
using namespace suite;
extern "C" void startup_probe();
extern "C" void startup_command_done();
extern "C" void recovery_disposing();
extern "C" void recovery_receipt_written();
extern "C" void recovery_terminal();
extern "C" void recovery_child_allocating();
extern "C" uint8_t startup_sample,startup_kind;
extern "C" volatile uint8_t startup_status;
volatile uint8_t startup_status=255;
static volatile uint8_t* const ram=reinterpret_cast<volatile uint8_t*>(0xb7e000);
// Private invocation state occupies capture-reserved A00-CFF, not a wire record.
struct Session {uint8_t magic[4],id[16],hashes[128],script[32],parent[16],disposition[32];uint8_t mask,index;uint32_t counts[8],length;char directory[64];uint32_t crc;};
static_assert(sizeof(Session)<768,"session SRAM reservation");
static Session session;
static char scratch[16384],script[8193];
static bool readfile(const char* path,void* data,size_t cap,size_t& n){FIL f={};if(ffs_fopen(&f,path,FA_READ))return false;uint32_t length=0;bool ok=!ffs_fsize(&f,&length)&&length<=cap;n=ok?ffs_fread(&f,static_cast<char*>(data),length):0;uint8_t err=ffs_ferror(&f),close=ffs_fclose(&f);return ok&&n==length&&!err&&!close;}
static bool savefile(const char* path,const void* data,size_t n){MosStorage f;if(f.open(path))return false;uint32_t status=0;bool ok=MosStorage::write(&f,static_cast<const uint8_t*>(data),n,&status)==n&&!status;if(ok)ok=!MosStorage::sync(&f);uint32_t close=MosStorage::close(&f);return ok&&!close;}
static bool hashfile(const char* path,uint8_t digest[32]){FIL f={};if(ffs_fopen(&f,path,FA_READ))return false;Sha256 h;char buf[512];while(!ffs_feof(&f)){size_t n=ffs_fread(&f,buf,sizeof buf);if(!n){ffs_fclose(&f);return false;}h.add(buf,n);}bool ok=!ffs_ferror(&f);ok=ffs_fclose(&f)==0&&ok;h.finish(digest);return ok;}
static bool copyfile(const char* source,const char* destination){FIL in={};if(ffs_fopen(&in,source,FA_READ))return false;MosStorage out;if(out.open(destination)){ffs_fclose(&in);return false;}char buf[512];bool ok=true;while(!ffs_feof(&in)){size_t n=ffs_fread(&in,buf,sizeof buf);uint32_t status=0;if(!n||MosStorage::write(&out,reinterpret_cast<uint8_t*>(buf),n,&status)!=n||status){ok=false;break;}}ok=!ffs_ferror(&in)&&ok;ok=ffs_fclose(&in)==0&&ok;if(ok)ok=!MosStorage::sync(&out);ok=MosStorage::close(&out)==0&&ok;return ok;}
static void path(char* dest,const char* name){snprintf(dest,128,"%s/%s",session.directory,name);}
static void remember(){memcpy(session.magic,"MSTS",4);session.crc=wire::crc(reinterpret_cast<const uint8_t*>(&session),offsetof(Session,crc));for(size_t i=0;i<sizeof session;++i)ram[0xa00+i]=reinterpret_cast<const uint8_t*>(&session)[i];}
static bool recall(){for(size_t i=0;i<sizeof session;++i)reinterpret_cast<uint8_t*>(&session)[i]=ram[0xa00+i];return !memcmp(session.magic,"MSTS",4)&&session.crc==wire::crc(reinterpret_cast<const uint8_t*>(&session),offsetof(Session,crc))&&session.directory[63]==0;}
static bool script_selection(Selection& selection,uint8_t digest[32]){size_t n=0;if(!readfile("/autoexec.txt",script,8192,n))return false;Sha256 h;h.add(script,n);h.finish(digest);script[n]=0;return parse_script(script,n,FUNCTIONS,selection);}
static bool allocation_intent();
static bool allocate(){uint8_t b[24];size_t n=0;if(!readfile("/mos-tests/install.bin",b,sizeof b,n)||n!=24||memcmp(b+20,"MSTI",4)||wire::get32(b+16)!=wire::crc(b,16))return false;
 uint64_t count=0;for(unsigned i=0;i<8;++i)count|=uint64_t(b[8+i])<<(8*i);if(count==UINT64_MAX)return false;++count;for(unsigned i=0;i<8;++i)b[8+i]=count>>(8*i);wire::put32(b+16,wire::crc(b,16));
 memcpy(session.id,b,16);if(!allocation_intent())return false;
 FIL f={};if(ffs_fopen(&f,"/mos-tests/install.bin",FA_WRITE))return false;uint8_t status=0;bool ok=recording_write(&f,reinterpret_cast<char*>(b),24,&status)==24&&!status;ok=!ffs_fsync(&f)&&ok;ok=ffs_fclose(&f)==0&&ok;if(!ok)return false;
 memcpy(session.id,b,16);char id[33];hex(b,16,id);snprintf(session.directory,sizeof session.directory,"/mos-tests/runs/%s",id);return ffs_mkdir(session.directory)==0;
}
static bool child_provenance();
static bool has_parent(){for(unsigned i=0;i<16;++i)if(session.parent[i])return true;return false;}
static int render_manifest(char* buffer,size_t cap,const uint8_t* id,const uint8_t* parent,const uint8_t* disposition,const uint8_t* hashes){
 char runid[33],parentid[33],d[65],h[4][65];hex(id,16,runid);hex(parent,16,parentid);hex(disposition,32,d);for(unsigned i=0;i<4;++i)hex(hashes+32*i,32,h[i]);
 bool child=false;for(unsigned i=0;i<16;++i)if(parent[i])child=true;
 if(child)return snprintf(buffer,cap,"{\"schema\":2,\"run_id\":\"%s\",\"parent_run_id\":\"%s\",\"bundle_sha256\":\"%s\",\"catalogue_sha256\":\"%s\",\"plan_sha256\":\"%s\",\"target_sha256\":\"%s\",\"disposition_sha256\":\"%s\"}\n",runid,parentid,h[0],h[1],h[2],h[3],d);
 return snprintf(buffer,cap,"{\"schema\":1,\"run_id\":\"%s\",\"parent_run_id\":null,\"bundle_sha256\":\"%s\",\"catalogue_sha256\":\"%s\",\"plan_sha256\":\"%s\",\"target_sha256\":\"%s\"}\n",runid,h[0],h[1],h[2],h[3]);
}
static bool prepare_files(){
 const char* manifests[3]={"bundle.json","catalogue.json","target.json"};const unsigned offsets[3]={0,32,96};char from[128],to[128];
 for(unsigned i=0;i<3;++i){snprintf(from,sizeof from,"/mos-tests/%s",manifests[i]);if(!hashfile(from,session.hashes+offsets[i]))return false;path(to,manifests[i]);if(i==0&&!has_parent()&&!copyfile(from,to))return false;}
 if(memcmp(session.hashes+32,CATALOGUE_DIGEST,32))return false;
 size_t n=0;if(!readfile("/mos-tests/bundle.json",scratch,sizeof scratch-1,n))return false;scratch[n]=0;
 uint8_t list_hash[32];char list_hex[65];if(!hashfile("/mos-tests/files.lst",list_hash))return false;hex(list_hash,32,list_hex);if(!strstr(scratch,list_hex))return false;
 if(!readfile("/mos-tests/files.lst",scratch,sizeof scratch-1,n))return false;scratch[n]=0;char* line=scratch;
 while(*line){char* end=strchr(line,'\n');if(!end)return false;*end=0;char* space=strchr(line,' ');if(!space)return false;*space++=0;
  if(!*line||strlen(line)>80||strchr(line,'/')||strstr(line,"..")||strlen(space)!=64)return false;
  snprintf(from,sizeof from,"/mos-tests/%s",line);uint8_t digest[32];char observed[65];if(!hashfile(from,digest))return false;hex(digest,32,observed);if(strcmp(observed,space))return false;path(to,line);if(!copyfile(from,to))return false;line=end+1;
 }
 path(to,"files.lst");if(!copyfile("/mos-tests/files.lst",to))return false;
 snprintf(from,sizeof from,"/mos-tests/plan-%u.json",session.mask);if(!readfile(from,scratch,sizeof scratch-1,n))return false;scratch[n]=0;
 char marker[65];memset(marker,'@',64);marker[64]=0;char* at=strstr(scratch,marker);if(!at||strstr(at+64,marker))return false;char sh[65];hex(session.script,32,sh);memcpy(at,sh,64);
 Sha256 hash;hash.add(scratch,n);hash.finish(session.hashes+64);path(to,"plan.json");if(!savefile(to,scratch,n))return false;
 path(to,"selection-script.txt");if(!savefile(to,script,strlen(script)))return false;
 if(has_parent()&&!child_provenance())return false;
 int len=render_manifest(scratch,sizeof scratch,session.id,session.parent,session.disposition,session.hashes);
 path(to,"run.json");return len>0&&size_t(len)<sizeof scratch&&savefile(to,scratch,len);
}
struct Context {RecordedLifecycle* bridge;uint8_t fault;};
static bool metadata(void*,const Case& c,wire::Payload& p){return p.case_start(2,CASE_HASHES[c.key-1]);}
static Result execute(void* data,const Case& c){auto& context=*static_cast<Context*>(data);unsigned failed=0;
 for(unsigned sample=0;sample<2;++sample){startup_sample=sample;startup_kind=c.key==2;startup_probe();uint8_t pair[96]={};for(unsigned i=0;i<64;++i)pair[i]=ram[0x900+i];memset(pair+64,255,20);if(c.key==2)pair[64+13]=0x7f;
  bool okay=true;for(unsigned i=0;i<20;++i){uint8_t expected=pair[i]^((c.key==2&&i==13)?128:0);if(pair[32+i]!=expected)okay=false;}if(!okay)++failed;
  wire::Payload p;if(!p.observation(1,sample,0,1,1,pair,96)||!context.bridge->observation(p))return {Outcome::Error,0,0,"capture checkpoint failed"};
 }
 if(context.fault==1&&c.key==1)++failed;
 return failed?Result{Outcome::Failed,3,failed,"synthetic control did not match its expected register effect (or deliberate qualification failure)"}:Result{Outcome::Passed,2,0,""};
}
static bool cleanup(void*,const Case&){return true;}
#include "recovery_target.h"
#include "recovery_disposition.h"
static bool child_provenance(){return recovery_target::prepare_child();}
static bool allocation_intent(){bool ok=recovery_target::publish(recovery::ALLOCATING,0,0,0);if(ok)recovery_child_allocating();return ok;}
static int command(int argc,char** argv){if(argc<2||!capture_available())return 19;
 if(argc==2&&!strcmp(argv[1],"recover"))return recovery_target::recover()?0:44;
 if(argc==2&&!strcmp(argv[1],"inspect")){if(!recovery_target::gate())return 41;printf("READY: recovery inspection permits a new run; no tests executed.\n");return 0;}
 Selection selection;uint8_t script_hash[32];if(!script_selection(selection,script_hash))return 20;
 bool begin=strcmp(argv[1],"begin")==0;
 if(begin){if(argc!=2)return 21;if(!recovery_target::gate())return 41;memset(&session,0,sizeof session);session.mask=selection.mask;memcpy(session.script,script_hash,32);if(!recovery_target::configure_child(selection))return 44;if(!allocate()||!prepare_files())return 22;
  MosStorage disk;char file[128];path(file,"results.bin");if(disk.open(file))return 23;Recorder r(ram,disk.adapter(),session.id,session.hashes+32,session.hashes+64);wire::Payload p;
  if(!r.begin()||!p.run_start(BACKEND,selection.count,session.hashes)||!r.append(1,p)||!r.checkpoint())return 24;
  uint32_t length=0;if(ffs_fsize(&disk.file,&length)||MosStorage::close(&disk)){r.fail(3,1,r.next-1);return 25;}session.length=length;if(!recovery_target::publish(recovery::BETWEEN,0,r.confirmed,length))return 42;remember();
  uint8_t fault=0;size_t fault_size=0;if(!readfile("/mos-tests/fault.bin",&fault,1,fault_size)||fault_size!=1)return 38;
  // Explicit qualification-only artifact: change a comment after plan persistence.
  if(fault==3){FIL change={};if(ffs_fopen(&change,"/autoexec.txt",FA_WRITE)||ffs_flseek(&change,2))return 39;uint8_t error=0;bool ok=recording_write(&change,"X",1,&error)==1&&!error;ok=ffs_fsync(&change)==0&&ok;ok=ffs_fclose(&change)==0&&ok;if(!ok)return 40;}
  printf("STARTED: %u synthetic tests; results in %s\n",selection.count,session.directory);return 0;
 }
 if(!recall()||session.mask!=selection.mask||memcmp(session.script,script_hash,32))return 26;
 if(!recovery_target::same_boot()){recovery_target::diagnose(9);return 43;}
 bool final=strcmp(argv[1],"finalize")==0;unsigned index=3;
 if(final){if(argc!=2||session.index!=selection.count)return 27;}
 else {if(argc!=3||strcmp(argv[1],"function"))return 28;for(unsigned i=0;i<3;++i)if(!strcmp(argv[2],FUNCTIONS[i]))index=i;if(session.index>=selection.count||index!=selection.order[session.index])return 29;}
 MosStorage disk;Recorder r(ram,disk.adapter(),session.id,session.hashes+32,session.hashes+64);if(!restore_ready(r)||r.confirmed!=recovery_target::latest().sequence())return 30;char file[128];path(file,"results.bin");
 if(ffs_fopen(&disk.file,file,FA_WRITE))return 31;disk.opened=true;uint32_t length=0;if(ffs_fsize(&disk.file,&length)||length!=session.length||ffs_flseek(&disk.file,length)){r.fail(5,6,r.next);return 32;}
 if(final){if(!recovery_target::publish(recovery::FINALIZING,0,r.confirmed,session.length))return 42;wire::Payload p;p.run_end(session.counts,session.hashes+64);if(!r.finish_run(p))return 33;FILINFO info={};if(ffs_stat(&info,file)||!recovery_target::publish(recovery::COMPLETE,0,r.confirmed,info.fsize))return 42;memset(session.magic,0,4);for(unsigned i=0;i<4;++i)ram[0xa00+i]=0;printf("COMPLETE: %lu passed, %lu failed, %lu unsupported. Decode saved evidence for the final report.\n",(unsigned long)session.counts[0],(unsigned long)session.counts[1],(unsigned long)session.counts[4]);return 0;}
 uint8_t fault=0;size_t size=0;if(!readfile("/mos-tests/fault.bin",&fault,1,size)||size!=1)return 34;
 if(fault==2){r.fail(5,7,r.next);return 35;}
 Context context{nullptr,fault};RecordedLifecycle bridge(r,&context,metadata,execute,cleanup);context.bridge=&bridge;const Case* chosen[]={&CASES[index]};auto hooks=bridge.hooks();hooks.start=recovery_target::case_start;hooks.finish=recovery_target::case_finish;auto totals=run(chosen,1,1,hooks);if(!totals.complete)return 36;
 for(unsigned i=0;i<8;++i)session.counts[i]+=totals.counts[i];++session.index;
 if(ffs_fsize(&disk.file,&length)||MosStorage::close(&disk)){r.fail(3,1,r.next-1);return 37;}session.length=length;if(!recovery_target::publish(recovery::BETWEEN,0,r.confirmed,length))return 42;remember();
 const char* outcome=totals.counts[0]?"PASSED":totals.counts[1]?"FAILED":"UNSUPPORTED";
 printf("%s: %s - %s\n",outcome,CASES[index].id,totals.counts[0]?(index==1?"changed only the expected IX upper bit in both samples":"preserved primary registers in both samples"):totals.counts[1]?"recorded a synthetic discrepancy; continuing selected groups":"required UART fixture is unavailable");return 0;
}
int main(int argc,char** argv){int result=command(argc,argv);startup_status=result;if(result)printf("ERROR: startup runner stopped with status %d; incomplete evidence is not a pass.\n",result);startup_command_done();return result;}
