#include "continuation.h"
#include <assert.h>
#include <stdio.h>
using namespace suite;
size_t write(void*,const uint8_t*,size_t n,uint32_t*){return n;}
uint32_t ok(void*){return 0;}
int main(){uint8_t ram[8192]={},id[16]={1},hash[32]={};Storage io{nullptr,write,ok,ok};Recorder r(ram,io,id,hash,hash);assert(r.begin());Recorder copy(ram,io,id,hash,hash);assert(restore_ready(copy));
 uint8_t saved[256];memcpy(saved,ram,256);
 auto reset=[&](){memcpy(ram,saved,256);};auto crc=[&](unsigned slot){wire::put32(ram+slot+120,wire::crc(ram+slot,120));};
 ram[124]=0;assert(!restore_ready(copy));reset();ram[8]=2;crc(0);assert(!restore_ready(copy));reset();ram[36]=1;crc(0);assert(!restore_ready(copy));reset();ram[38]=4;crc(0);assert(!restore_ready(copy));reset();ram[28]=4;crc(0);assert(!restore_ready(copy));reset();ram[108]=1;crc(0);assert(!restore_ready(copy));reset();
 memcpy(ram+128,ram,128);ram[128+38]=5;crc(128);assert(!restore_ready(copy));reset();memcpy(ram+128,ram,128);wire::put32(ram+128+24,2);ram[128+38]=5;crc(128);assert(!restore_ready(copy));
 puts("PASSED: clean continuation and eight corrupt/unsafe control boundaries.");}
