#pragma once
#include "bounded_json.h"
namespace recovery_target {
using bounded_json::Document;using bounded_json::Writer;
static Document json;
static char json_text[16385],request_reason[513],request_actor[129];
struct Receipt {uint64_t generation;uint8_t digest[32],subject[16],script[32],action,mask;};
struct RecoveryFile {char name[32];uint8_t digest[32];bool covered;};
static Receipt receipts[64];static unsigned receipt_count=0,file_count=0;
static RecoveryFile recovery_files[256];
inline void generation_name(uint64_t n,char* out){const char* digits="0123456789abcdef";for(unsigned i=0;i<16;++i)out[i]=digits[(n>>(4*(15-i)))&15];out[16]=0;}
inline void decimal_text(uint64_t n,char* out){char reverse[21];unsigned used=0;do{reverse[used++]='0'+n%10;n/=10;}while(n);for(unsigned i=0;i<used;++i)out[i]=reverse[used-i-1];out[used]=0;}
inline bool json_hex(int token,uint8_t* out,size_t size){char value[129];return token>=0&&json.string(token,value,sizeof value)&&from_hex(value,out,size);}
inline bool selected_ids(int token,unsigned& mask){
 if(token<0||json.nodes[token].kind!='[')return false;mask=0;unsigned previous=0;
 for(unsigned i=token+1;i<json.nodes[token].next;i=json.nodes[i].next){char name[96];if(!json.string(i,name,sizeof name))return false;unsigned key=0;for(unsigned j=0;j<3;++j)if(!strcmp(name,CASES[j].id))key=j+1;
  if(!key||key<=previous)return false;previous=key;mask|=1<<(key-1);
 }return true;
}
inline bool action_value(int token,uint8_t& action){char name[16];if(token<0||!json.string(token,name,sizeof name))return false;action=!strcmp(name,"park")?1:!strcmp(name,"retry")?2:!strcmp(name,"continue")?3:0;return action!=0;}
inline bool receipt_fields(Receipt& r,bool request){
 const char* req[]={"schema","subject_run_id","journal_generation","action","case_ids","script_sha256","actor","reason","prerequisites_confirmed"};
 const char* rec[]={"schema","installation_namespace","subject_run_id","journal_generation","action","case_ids","selection_script_sha256","evidence_sha256","reason","actor","prerequisites_confirmed"};
 if(!json.fields(0,request?req:rec,request?9:11)||!json.literal(json.get(0,"schema"),"1")||
    !json_hex(json.get(0,"subject_run_id"),r.subject,16)||memcmp(r.subject,allocation,8)||
    !json.generation(json.get(0,"journal_generation"),r.generation)||!action_value(json.get(0,"action"),r.action))return false;
 unsigned mask=0;if(!selected_ids(json.get(0,"case_ids"),mask))return false;r.mask=mask;
 int script=json.get(0,request?"script_sha256":"selection_script_sha256");
 memset(r.script,0,32);
 if(r.action==1){if(mask||!json.literal(script,"null"))return false;}
 else if(!mask||!json_hex(script,r.script,32)||!json.literal(json.get(0,"prerequisites_confirmed"),"true"))return false;
 if(!json.literal(json.get(0,"prerequisites_confirmed"),"true")&&!json.literal(json.get(0,"prerequisites_confirmed"),"false"))return false;
 if(!json.string(json.get(0,"actor"),request_actor,sizeof request_actor)||!*request_actor||
    !json.string(json.get(0,"reason"),request_reason,sizeof request_reason)||!*request_reason)return false;
 if(!request){uint8_t ns[8];if(!json_hex(json.get(0,"installation_namespace"),ns,8)||memcmp(ns,allocation,8))return false;}
 return true;
}
inline bool load_json(const char* path){size_t n=0;return readfile(path,json_text,16384,n)&&json.parse(json_text,n);}
inline bool safe_evidence(const char* path){
 if(!*path||*path=='/'||strchr(path,'\\')||strstr(path,".."))return false;
 return !strncmp(path,"runs/",5)||!strncmp(path,"recovery/",9);
}
inline bool verify_evidence(const Receipt& receipt){
 int map=json.get(0,"evidence_sha256");if(map<0||json.nodes[map].kind!='{')return false;
 unsigned count=0;char key[256],path[280];uint8_t digest[32];
 for(unsigned i=map+1;i<json.nodes[map].next;i=json.nodes[i+1].next){
  if(++count>200||!json.string(i,key,sizeof key)||!safe_evidence(key)||!json_hex(i+1,digest,32))return false;
  snprintf(path,sizeof path,"/mos-tests/%s",key);if(!digest_match(path,digest))return false;
  if(!strncmp(key,"recovery/",9))for(unsigned f=0;f<file_count;++f)if(!strcmp(key+9,recovery_files[f].name)&&!memcmp(digest,recovery_files[f].digest,32))recovery_files[f].covered=true;
 }
 char stem[17],snapshot_path[100],relative[80];generation_name(receipt.generation,stem);Slot original[2];size_t size=0;
 for(unsigned s=0;s<2;++s){snprintf(relative,sizeof relative,"recovery/%s-%c.bin",stem,'a'+s);if(json.get(map,relative)<0)return false;
  snprintf(snapshot_path,sizeof snapshot_path,"/mos-tests/%s",relative);if(!readfile(snapshot_path,original[s].b,256,size)||size!=256)return false;}
 unsigned selected=0;if(!pair(original[0],original[1],selected)||original[selected].generation()==UINT64_MAX||
  original[selected].generation()+1!=receipt.generation||memcmp(original[selected].b+24,receipt.subject,16))return false;
 // Every subject file must be committed, not merely an arbitrary subset.
 char subject[33],directory[80];hex(receipt.subject,16,subject);snprintf(directory,sizeof directory,"/mos-tests/runs/%s",subject);
 DIR dir={};FILINFO entry={};if(ffs_dopen(&dir,directory))return false;bool ok=true;unsigned seen=0;
 while(ok){if(ffs_dread(&dir,&entry)){ok=false;break;}if(!entry.fname[0])break;
  if(++seen>128||(entry.fattrib&0x10)){ok=false;break;}
  snprintf(key,sizeof key,"runs/%s/%s",subject,entry.fname);if(json.get(map,key)<0)ok=false;
 }
 return ffs_dclose(&dir)==0&&ok&&seen>0;
}
inline bool collect_receipts(bool allow_orphans){
 receipt_count=0;file_count=0;DIR dir={};FILINFO entry={};uint8_t opened=ffs_dopen(&dir,"/mos-tests/recovery");
 if(opened==4||opened==5)return true;if(opened)return false;bool ok=true;
 while(ok){if(ffs_dread(&dir,&entry)){ok=false;break;}if(!entry.fname[0])break;
  if(file_count==256||(entry.fattrib&0x10)||strlen(entry.fname)>31||strlen(entry.fname)<20){ok=false;break;}
  char generation[17];memcpy(generation,entry.fname,16);generation[16]=0;uint8_t value[8];
  const char* suffix=entry.fname+16;
  if(!from_hex(generation,value,8)||(strcmp(suffix,".json")&&strcmp(suffix,".accepted")&&strcmp(suffix,"-a.bin")&&strcmp(suffix,"-b.bin"))){ok=false;break;}
  auto& f=recovery_files[file_count++];strcpy(f.name,entry.fname);f.covered=false;
  char path[80];snprintf(path,sizeof path,"/mos-tests/recovery/%s",f.name);if(!bounded_hash(path,f.digest))ok=false;
 }
 bool closed=ffs_dclose(&dir)==0;if(!ok||!closed)return false;
 // Parse certificates first. Invalid/partial files can only be accounted for by
 // a later explicit disposition; they never authorize a subject themselves.
 for(unsigned i=0;i<file_count;++i){
  auto& f=recovery_files[i];if(strcmp(f.name+16,".accepted"))continue;
  char path[80];snprintf(path,sizeof path,"/mos-tests/recovery/%s",f.name);uint8_t certificate[256];size_t n=0;
  if(!readfile(path,certificate,256,n)||n!=256||memcmp(certificate,"MSTA",4)||u16(certificate+4)!=1||u16(certificate+6)!=256||
   !zero(certificate+66,2)||!zero(certificate+100,148)||!zero(certificate+253,3)||certificate[252]!=0xa5||
   wire::get32(certificate+248)!=wire::crc(certificate,248))continue;
  if(receipt_count==64)return false;
  Receipt r={};char stem[17];generation_name(u64(certificate+8),stem);if(strncmp(stem,f.name,16))return false;
  snprintf(path,sizeof path,"/mos-tests/recovery/%s.json",stem);
  if(!bounded_hash(path,r.digest)||memcmp(r.digest,certificate+16,32)||!load_json(path)||!receipt_fields(r,false)||
   r.generation!=u64(certificate+8)||memcmp(r.subject,certificate+48,16)||r.action!=certificate[64]||r.mask!=certificate[65]||
   memcmp(r.script,certificate+68,32)||!verify_evidence(r))return false;
  receipts[receipt_count++]=r;f.covered=true;
  for(unsigned j=0;j<file_count;++j)if(!strncmp(recovery_files[j].name,stem,16))recovery_files[j].covered=true;
 }
 if(!allow_orphans)for(unsigned i=0;i<file_count;++i)if(!recovery_files[i].covered)return false;
 return true;
}
inline Receipt* receipt_by_hash(const uint8_t* digest){for(unsigned i=0;i<receipt_count;++i)if(!memcmp(receipts[i].digest,digest,32))return &receipts[i];return nullptr;}
inline bool accepted_parent(const uint8_t* id){for(unsigned i=0;i<receipt_count;++i)if(!memcmp(receipts[i].subject,id,16))return true;return false;}
inline bool armed_valid(){auto* r=receipt_by_hash(latest().b+148);return r&&(r->action==2||r->action==3)&&r->action==latest().b[121]&&!memcmp(r->subject,latest().b+24,16)&&!memcmp(r->script,latest().b+88,32);}
inline bool configure_child(const Selection& selection){
 if(latest().phase()!=ARMED)return true;auto* r=receipt_by_hash(latest().b+148);
 if(!armed_valid()||!r||selection.mask!=r->mask||memcmp(session.script,r->script,32))return false;
 memcpy(session.parent,r->subject,16);memcpy(session.disposition,r->digest,32);return true;
}
inline bool child_metadata(const char* directory,uint8_t* parent,uint8_t* digest,unsigned mask,const uint8_t* script){
 char path[160];snprintf(path,sizeof path,"%s/disposition.json",directory);FILINFO info={};uint8_t status=ffs_stat(&info,path);
 if(status==4)return true;if(status||!bounded_hash(path,digest))return false;
 auto* r=receipt_by_hash(digest);if(!r||r->action==1||r->mask!=mask||memcmp(script,r->script,32))return false;
 memcpy(parent,r->subject,16);return true;
}
inline bool child_bundle(const char* receipt_path,uint8_t* digest,bool save){
 size_t n=0;if(!readfile("/mos-tests/bundle.json",compare_text,sizeof compare_text-1,n))return false;compare_text[n]=0;
 const char* ending="\n  ]\n}\n";size_t tail=strlen(ending);if(n<tail||strcmp(compare_text+n-tail,ending))return false;
 uint8_t receipt_digest[32];if(!bounded_hash(receipt_path,receipt_digest))return false;
 FILINFO info={};if(ffs_stat(&info,receipt_path))return false;char h[65],part[240];hex(receipt_digest,32,h);
 int size=snprintf(part,sizeof part,",\n    {\n      \"path\": \"disposition.json\",\n      \"size\": %lu,\n      \"sha256\": \"%s\"\n    }\n  ]\n}\n",(unsigned long)info.fsize,h);
 if(size<0||n-tail+size>=sizeof compare_text)return false;memcpy(compare_text+n-tail,part,size);n=n-tail+size;
 Sha256 sha;sha.add(compare_text,n);sha.finish(digest);
 if(save){char output[128];path(output,"bundle.json");if(!savefile(output,compare_text,n))return false;}
 return true;
}
inline bool prepare_child(){
 auto* r=receipt_by_hash(session.disposition);if(!r)return false;char stem[17],from[96],to[128];generation_name(r->generation,stem);
 snprintf(from,sizeof from,"/mos-tests/recovery/%s.json",stem);path(to,"disposition.json");
 return copyfile(from,to)&&child_bundle(from,session.hashes,true);
}
inline bool add_hash(Writer& writer,const char* relative){
 char path[300],digest[65];uint8_t h[32];snprintf(path,sizeof path,"/mos-tests/%s",relative);
 if(!checked_hash(path,h,1048576UL))return false;hex(h,32,digest);
 if(writer.used&&writer.data[writer.used-1]!='{')writer.raw(",");writer.string(relative);writer.raw(":");writer.string(digest);return writer.ok;
}
inline bool recover(){
 memset(recovery_diagnostic,0,64);recovery_diagnostic[1]=255;hashed_bytes=0;inspected_bytes=0;
 if(!load()||latest().phase()==IDLE||latest().phase()==COMPLETE||latest().generation()>UINT64_MAX-2){diagnose(10);return false;}
 if(!load_json("/mos-tests/request.json")){diagnose(11);return false;}Receipt request={};
 if(!receipt_fields(request,true)||request.generation!=latest().generation()||memcmp(request.subject,latest().b+24,16)){diagnose(11);return false;}
 // collect/inspect parse receipts into the same JSON scratch; save human fields.
 char actor[129],reason[513];strcpy(actor,request_actor);strcpy(reason,request_reason);
 if(latest().counter()!=u64(allocation+8)||!collect_receipts(true)){diagnose(10);return false;}
 char id[33],directory[80];hex(request.subject,16,id);snprintf(directory,sizeof directory,"/mos-tests/runs/%s",id);
 bool complete=false;uint32_t seq=0,length=0;if(!inspect_run(directory,request.subject,complete,seq,length)){diagnose(10);return false;}
 if(request.action!=1){
  Selection selected;uint8_t hash[32];if(!script_selection(selected,hash)||selected.mask!=request.mask||memcmp(hash,request.script,32)||
   (request.mask&~last_mask)||(request.action==3&&(request.mask&last_ended))){diagnose(11);return false;}
 }
 Slot original[2]={slots[0],slots[1]},next=latest();put64(next.b+16,next.generation()+1);next.b[120]=DISPOSING;next.b[121]=request.action;
 wire::put32(next.b+128,seq);put64(next.b+132,length);memset(next.b+148,0,32);
 if(!commit_slot(next)){diagnose(10);return false;}
 recovery_disposing();
 uint64_t generation=latest().generation();char stem[17],where[96];generation_name(generation,stem);
 DIR existing={};uint8_t found=ffs_dopen(&existing,"/mos-tests/recovery");if(!found){if(ffs_dclose(&existing)){diagnose(10);return false;}}
 else if((found!=4&&found!=5)||ffs_mkdir("/mos-tests/recovery")){diagnose(10);return false;}
 for(unsigned i=0;i<2;++i){snprintf(where,sizeof where,"/mos-tests/recovery/%s-%c.bin",stem,'a'+i);if(!savefile(where,original[i].b,256)){diagnose(10);return false;}}
 Writer writer(json_text,sizeof json_text);char ns[17],gen[24],script_hash[65];hex(allocation,8,ns);decimal_text(generation,gen);hex(request.script,32,script_hash);
 writer.raw("{\"schema\":1,\"installation_namespace\":");writer.string(ns);writer.raw(",\"subject_run_id\":");writer.string(id);
 writer.raw(",\"journal_generation\":");writer.string(gen);writer.raw(",\"action\":");writer.string(request.action==1?"park":request.action==2?"retry":"continue");
 writer.raw(",\"case_ids\":[");bool first=true;for(unsigned i=0;i<3;++i)if(request.mask&(1<<i)){if(!first)writer.raw(",");writer.string(CASES[i].id);first=false;}
 writer.raw("],\"selection_script_sha256\":");if(request.action==1)writer.raw("null");else writer.string(script_hash);
 writer.raw(",\"evidence_sha256\":{");first=true;
 DIR dir={};FILINFO entry={};if(ffs_dopen(&dir,directory)){diagnose(10);return false;}bool ok=true;unsigned entries=0;
 while(ok){if(ffs_dread(&dir,&entry)){ok=false;break;}if(!entry.fname[0])break;if(++entries>128||(entry.fattrib&0x10)){ok=false;break;}
  char relative[300];snprintf(relative,sizeof relative,"runs/%s/%s",id,entry.fname);if(!add_hash(writer,relative))ok=false;
 }
 bool closed=ffs_dclose(&dir)==0;if(!ok||!closed){diagnose(10);return false;}
 for(unsigned i=0;i<file_count;++i){char relative[80];snprintf(relative,sizeof relative,"recovery/%s",recovery_files[i].name);if(!add_hash(writer,relative)){diagnose(10);return false;}}
 for(unsigned i=0;i<2;++i){char relative[80];snprintf(relative,sizeof relative,"recovery/%s-%c.bin",stem,'a'+i);if(!add_hash(writer,relative)){diagnose(10);return false;}}
 writer.raw("},\"reason\":");writer.string(reason);writer.raw(",\"actor\":");writer.string(actor);
 writer.raw(",\"prerequisites_confirmed\":");writer.raw(request.action==1?"false":"true");writer.raw("}\n");
 snprintf(where,sizeof where,"/mos-tests/recovery/%s.json",stem);uint8_t digest[32];Sha256 sha;sha.add(json_text,writer.used);sha.finish(digest);
 Receipt checked={};
 if(!writer.ok||!json.parse(json_text,writer.used)||!receipt_fields(checked,false)||!verify_evidence(checked)||!savefile(where,json_text,writer.used)||!digest_match(where,digest)){diagnose(10);return false;}
 recovery_receipt_written();
 next=latest();put64(next.b+16,next.generation()+1);next.b[120]=request.action==1?PARKED:ARMED;memcpy(next.b+148,digest,32);
 if(request.action!=1)memcpy(next.b+88,request.script,32);
 if(!commit_slot(next)){diagnose(10);return false;}
 recovery_terminal();
 uint8_t certificate[256]={};memcpy(certificate,"MSTA",4);wire::put16(certificate+4,1);wire::put16(certificate+6,256);put64(certificate+8,generation);
 memcpy(certificate+16,digest,32);memcpy(certificate+48,request.subject,16);certificate[64]=request.action;certificate[65]=request.mask;memcpy(certificate+68,request.script,32);
 wire::put32(certificate+248,wire::crc(certificate,248));certificate[252]=0xa5;
 snprintf(where,sizeof where,"/mos-tests/recovery/%s.accepted",stem);uint8_t check[256];size_t size=0;
 if(!savefile(where,certificate,256)||!readfile(where,check,256,size)||size!=256||memcmp(check,certificate,256)){diagnose(10);return false;}
 recovery_diagnostic[0]=0;recovery_diagnostic[1]=latest().phase();
 printf("%s: explicit disposition recorded; original run remains unchanged.\n",request.action==1?"PARKED":"ARMED");
 return true;
}
}
