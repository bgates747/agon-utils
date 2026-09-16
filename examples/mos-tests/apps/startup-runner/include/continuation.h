#pragma once
#include "recording.h"
// Resume only a clean same-boot command boundary; never an uncertain file tail.
inline bool restore_ready(suite::Recorder& r) {
 uint8_t b[2][128];int best=-1;
 for(unsigned s=0;s<2;++s){
  auto p=b[s];for(unsigned i=0;i<128;++i)p[i]=r.ram[s*128+i];
  if(memcmp(p,"MSTC\1\0\200\0",8)||p[124]!=0xa5||suite::wire::get32(p+120)!=suite::wire::crc(p,120))continue;
  if(memcmp(p+8,r.run_id,16)||memcmp(p+44,r.catalogue,32)||memcmp(p+76,r.plan,32))return false;
  if(p[39]||p[125]||p[126]||p[127]||!suite::wire::get32(p+24))return false;
  for(unsigned i=108;i<120;++i)if(p[i])return false;
  if(best>=0&&suite::wire::get32(p+24)==suite::wire::get32(b[best]+24)&&memcmp(p,b[best],128))return false;
  if(best<0||suite::wire::get32(p+24)>suite::wire::get32(b[best]+24))best=s;
 }
 if(best<0)return false;auto p=b[best];
 if(p[38]!=1||p[36]||p[37]||suite::wire::get32(p+40))return false;
 uint32_t next=suite::wire::get32(p+28),confirmed=suite::wire::get32(p+32);
 if(!next||confirmed==UINT32_MAX||next!=confirmed+1)return false;
 r.generation=suite::wire::get32(p+24);r.next=next;r.confirmed=confirmed;r.slot=best;return true;
}
