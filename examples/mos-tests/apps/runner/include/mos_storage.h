#pragma once
#include <agon/mos.h>
#include "recording.h"
extern "C" uint24_t recording_write(FIL*,const char*,uint24_t,uint8_t*);
namespace suite {
struct MosStorage {
 FIL file={};bool opened=false;
 uint32_t open(const char* path) {uint8_t status=ffs_fopen(&file,path,FA_WRITE|FA_CREATE_NEW);opened=status==0;return status;}
 static size_t write(void* ctx,const uint8_t* b,size_t n,uint32_t* status) {
  auto& s=*static_cast<MosStorage*>(ctx);uint8_t result=0;
  size_t written=recording_write(&s.file,reinterpret_cast<const char*>(b),n,&result);
  *status=result;return written;
 }
 static uint32_t sync(void* ctx) {return ffs_fsync(&static_cast<MosStorage*>(ctx)->file);}
 static uint32_t close(void* ctx) {auto& s=*static_cast<MosStorage*>(ctx);uint32_t result=ffs_fclose(&s.file);if(!result)s.opened=false;return result;}
 Storage adapter() {return {this,write,sync,close};}
};
}
