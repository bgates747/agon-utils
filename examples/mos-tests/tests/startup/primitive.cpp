#include "sha256.h"
#include "script.h"
#include <stdio.h>
int main(int argc,char** argv){char b[8193];size_t n=fread(b,1,sizeof b,stdin);if(argc>1){const char* f[]={"synthetic_preserve","synthetic_clobber","synthetic_capability"};Selection s;if(!parse_script(b,n,f,s))return 2;printf("%u\n",s.mask);}else{Sha256 h;h.add(b,n);uint8_t d[32];char o[65];h.finish(d);hex(d,32,o);puts(o);}return 0;}
