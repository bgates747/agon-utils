#include "recovery.h"
#include <cassert>
#include <cstdio>
#include <vector>
using namespace recovery;
static std::vector<uint8_t> read(const char* name){FILE* f=fopen(name,"rb");assert(f);std::vector<uint8_t> b;int c;while((c=fgetc(f))!=EOF)b.push_back(c);assert(!ferror(f));fclose(f);return b;}
int main(int argc,char** argv){
 if(argc==3&&!strcmp(argv[1],"records")){
  auto b=read(argv[2]);if(b.size()<338)return 3;
  uint8_t contracts[3][64];memcpy(contracts,b.data()+144,192);
  Records r(b.data(),b.data()+16,contracts,b[336]);size_t pos=338;
  while(pos<b.size()){
   if(b.size()-pos<40)return 2;uint32_t n=suite::wire::get32(b.data()+pos+32);
   if(n>1024||n<2||n+45>b.size()-pos||!r.accept(b.data()+pos,n+45))return 2;pos+=n+45;
  }
  printf("%lu %lu %lu\n",(unsigned long)r.sequence,(unsigned long)r.failed_mask,(unsigned long)r.current);
  return r.complete?0:2;
 }
 assert(argc==2);auto b=read(argv[1]);assert(b.size()==256);Slot sample;memcpy(sample.b,b.data(),256);assert(sample.valid()&&sample.phase()==IDLE&&sample.generation()==2);
 for(unsigned bit=0;bit<2048;++bit){Slot bad=sample;bad.b[bit/8]^=1<<(bit%8);assert(!bad.valid());}
 Slot a=sample;put64(a.b+16,1);a.seal();unsigned selected=9;assert(pair(a,sample,selected)&&selected==1);
 Slot bad=sample;bad.b[8]^=1;bad.seal();assert(!pair(a,bad,selected));
 bad=sample;put64(bad.b+16,4);bad.seal();assert(!pair(a,bad,selected));
 bad=sample;bad.b[180]=1;bad.seal();assert(!bad.valid());
 bad=sample;bad.b[120]=255;bad.seal();assert(!bad.valid());
 bad=sample;bad.b[121]=4;bad.seal();assert(!bad.valid());
 assert(pair(sample,sample,selected));bad=sample;bad.b[8]^=1;bad.seal();assert(!pair(sample,bad,selected));
 const unsigned edges[][2]={{0,0},{0,1},{1,2},{1,8},{2,3},{2,6},{2,8},{3,4},{3,8},{4,5},{4,8},{5,2},{5,8},{6,7},{6,8},{7,1},{8,8},{8,9},{8,10},{9,8},{10,8},{10,1}};
 for(unsigned x=0;x<11;++x)for(unsigned y=0;y<11;++y){bool expected=false;for(auto& e:edges)if(e[0]==x&&e[1]==y)expected=true;assert(edge(x,y)==expected);}
 puts("PASSED: independent IDLE fixture, 2048 bit corruptions, semantic/pair rejection and 121 transition decisions.");
}
