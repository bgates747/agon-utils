#pragma once
#include <string.h>
#include <stddef.h>
// Generated subset only: no shell emulation, bounded input, canonical function order.
struct Selection {unsigned mask=0;unsigned order[3]={};unsigned count=0;};
inline bool parse_script(const char* text,size_t size,const char* const* functions,Selection& out) {
 if(!size||size>8192)return false;bool load=false,begin=false,end=false;unsigned previous=0;char line[256];size_t pos=0;
 while(pos<size){size_t n=0;while(pos<size&&text[pos]!='\n'){if(n==255||!text[pos])return false;line[n++]=text[pos++];}if(pos<size)++pos;
  while(n&&(line[n-1]=='\r'||line[n-1]==' '||line[n-1]=='\t'))--n;line[n]=0;char* s=line;while(*s==' '||*s=='\t')++s;
  if(!*s||*s=='#')continue;if(end)return false;
  if(strcmp(s,"LOAD /mos-tests/runner.bin")==0){if(load)return false;load=true;continue;}
  if(!load)return false;load=false;
  if(strcmp(s,"RUN . begin")==0){if(begin)return false;begin=true;continue;}
  if(!begin)return false;
  if(strcmp(s,"RUN . finalize")==0){if(!out.count)return false;end=true;continue;}
  const char* prefix="RUN . function ";if(strncmp(s,prefix,strlen(prefix)))return false;
  unsigned found=3;for(unsigned i=0;i<3;++i)if(strcmp(s+strlen(prefix),functions[i])==0)found=i;
  if(found==3||(out.mask&(1<<found))||(out.count&&found<previous))return false;
  out.mask|=1<<found;out.order[out.count++]=found;previous=found;
 }
 return begin&&end&&!load;
}
