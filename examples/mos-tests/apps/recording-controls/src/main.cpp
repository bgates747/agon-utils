#include "mos_storage.h"
#include "recorded_lifecycle.h"
#include "capture.h"
#include <stdio.h>
extern "C" void recording_probe();
extern "C" void recording_done();
extern "C" volatile uint8_t recording_status;
volatile uint8_t recording_status=0;
using namespace suite;
static uint8_t run_id[16],hashes[128];
static MosStorage disk;
struct Context {RecordedLifecycle* bridge;};
bool metadata(void*,const Case&,wire::Payload& p) {return p.case_start(1,hashes);}
Result execute(void* v,const Case&) {
 // No storage/reporting occurs between paired captures. Seed after checkpoint.
 recording_probe();uint8_t data[96]={};auto ram=reinterpret_cast<volatile uint8_t*>(0xb7e900);
 for(unsigned i=0;i<64;++i)data[i]=ram[i];for(unsigned i=0;i<20;++i)data[64+i]=0xff;
 bool same=memcmp(data,data+32,20)==0;wire::Payload p;
 if(!p.observation(1,0,0,1,1,data,96)||!static_cast<Context*>(v)->bridge->observation(p))return {Outcome::Error,0,0,"observation checkpoint failed"};
 return same?Result{Outcome::Passed,1,0,""}:Result{Outcome::Failed,1,1,"preserving control changed primary state"};
}
bool cleanup(void*,const Case&) {return true;}
int main() {
 if(!capture_available())return 19;
 // Fixture host allocates identity on a fresh exclusive run directory and raw image.
 FIL input={};if(ffs_fopen(&input,"/run.id",FA_READ))return 20;
 auto n=ffs_fread(&input,reinterpret_cast<char*>(run_id),16);auto close=ffs_fclose(&input);if(n!=16||close)return 21;
 auto ram=reinterpret_cast<volatile uint8_t*>(0xb7e000);
 for(unsigned i=0;i<8192;++i)ram[i]=0xc7;
 for(unsigned i=0;i<128;++i)hashes[i]=uint8_t(0x11*(i/32+1));
 Recorder recorder(ram,disk.adapter(),run_id,hashes+32,hashes+64);
 if(!recorder.begin())return 22;
 uint32_t status=disk.open("/results.bin");if(status){recorder.fail(5,status,1);recording_status=2;recording_done();return 23;}
 wire::Payload p;if(!p.run_start(1,2,hashes)||!recorder.append(1,p)||!recorder.checkpoint()){recording_status=3;recording_done();return 24;}
 Context context{};RecordedLifecycle bridge(recorder,&context,metadata,execute,cleanup);context.bridge=&bridge;
 Case a={1,"checkpoint.preserve.1","synthetic","controls",0},b={2,"checkpoint.preserve.2","synthetic","controls",0};const Case* plan[]={&a,&b};
 auto totals=run(plan,2,0,bridge.hooks());
 if(totals.complete){p.run_end(totals.counts,hashes+64);if(recorder.finish_run(p))recording_status=1;}
 if(!recording_status)recording_status=4;
 recording_done();return recording_status==1?0:25;
}
