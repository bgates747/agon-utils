#pragma once
// stdio ownership adapter for the bounded plain-buffer reader.
#include "agnb_buffers.hpp"
#include <stdio.h>
#include <limits.h>

namespace agnb {
namespace detail {
inline Error file_read(void *context,uint8_t *out,uint16_t count) {
    if(!count)return Error::Ok;
    FILE *file=static_cast<FILE*>(context);
    if(fread(out,1,count,file)==count)return Error::Ok;
    return ferror(file)?Error::Read:Error::Eof;
}
}
// Owns opening/closing the file. Uses signed-long stdio positions; rejects
// failures/overflow instead of narrowing a complete file to the target's int.
inline Error load_buffers_file(const char *filename,Transport transport,Workspace &workspace,
                               Completed completed=nullptr,void *context=nullptr) {
    FILE *file=fopen(filename,"rb");if(!file)return Error::Open;
    Error error=Error::Ok;long size=0;
    if(fseek(file,0,SEEK_END)!=0||(size=ftell(file))<0||fseek(file,0,SEEK_SET)!=0)error=Error::Seek;
    else if(static_cast<unsigned long>(size)>UINT32_MAX)error=Error::Bounds;
    else error=load_buffers({file,detail::file_read,static_cast<uint32_t>(size)},transport,workspace,completed,context);
    const int closed=fclose(file);
    return error!=Error::Ok?error:closed?Error::Close:Error::Ok;
}
} // namespace agnb
