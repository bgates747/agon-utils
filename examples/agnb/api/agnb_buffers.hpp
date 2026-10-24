#pragma once
// AGNB0.3 bounded plain-buffer reader. Brandon R. Gates.
// No heap, runtime ID allocation, implicit calls or payload interpretation.
#include <stdint.h>

namespace agnb {
enum class Error : uint8_t {
    Ok=0, Open=1, Read=2, Seek=3, RiffId=4, Form=5, Version=6, Chunk=7,
    Bounds=8, BufferId=9, Metadata=10, DataSize=11, Transport=12, Eof=13, Close=14
};
struct Record { uint16_t buffer_id; uint32_t data_bytes; };
struct Workspace { uint8_t data[8192]; };
// read must fill exactly count bytes, or return Read/Eof; partial input may be consumed.
struct Input {
    void *context;
    Error (*read)(void *,uint8_t *,uint16_t);
    uint32_t bytes;
};
// send consumes all count bytes before returning, in stream order. It must
// not retain the pointer. True does not acknowledge VDP memory.
struct Transport { void *context; bool (*send)(void *,const uint8_t *,uint16_t); };
using Completed = void (*)(void *,const Record &);

namespace detail {
inline uint16_t word(const uint8_t *p){return uint16_t(p[0])|(uint16_t(p[1])<<8);}
inline uint32_t dword(const uint8_t *p){return uint32_t(word(p))|(uint32_t(word(p+2))<<16);}
inline bool fourcc(const uint8_t *p,const char *s){return p[0]==s[0]&&p[1]==s[1]&&p[2]==s[2]&&p[3]==s[3];}
struct Chunk { uint32_t bytes,end,next; };
class Reader {
    Input input_;
public:
    uint32_t at=0;
    explicit Reader(Input input):input_(input){}
    Error read(uint8_t *out,uint16_t count,uint32_t boundary) {
        if(at>boundary||uint32_t(count)>boundary-at)return Error::Bounds;
        if(!count)return Error::Ok;
        Error e=input_.read(input_.context,out,count);
        if(e==Error::Ok)at+=count;
        return e;
    }
    Error chunk(const char *id,uint32_t boundary,Chunk &c) {
        uint8_t header[8];Error e=read(header,8,boundary);if(e!=Error::Ok)return e;
        if(!fourcc(header,id))return Error::Chunk;
        c.bytes=dword(header+4);
        const uint32_t pad=(0u-c.bytes)&3u;
        if(c.bytes>boundary-at||pad>boundary-at-c.bytes)return Error::Bounds;
        c.end=at+c.bytes;c.next=c.end+pad;return Error::Ok;
    }
    Error padding(const Chunk &c) {
        uint8_t pad[3]={0,0,0};
        if(at!=c.end)return Error::Bounds;
        Error e=read(pad,uint16_t(c.next-c.end),c.next);if(e!=Error::Ok)return e;
        return (pad[0]|pad[1]|pad[2])?Error::Chunk:Error::Ok;
    }
};
inline bool command(Transport t,uint16_t id,uint8_t op) {
    const uint8_t packet[]={23,0,160,uint8_t(id),uint8_t(id>>8),op};
    return t.send(t.context,packet,sizeof packet);
}
} // namespace detail

inline Error load_buffers(Input input,Transport transport,Workspace &workspace,
                          Completed completed=nullptr,void *callback_context=nullptr) {
    if(!input.read||!transport.send)return Error::Metadata;
    detail::Reader r(input);uint8_t header[12];
    Error e=r.read(header,12,input.bytes);if(e!=Error::Ok)return e;
    if(!detail::fourcc(header,"RIFF"))return Error::RiffId;
    if(!detail::fourcc(header+8,"AGNB"))return Error::Form;
    if(detail::dword(header+4)!=input.bytes-8)return Error::Bounds;
    detail::Chunk vers;
    e=r.chunk("VERS",input.bytes,vers);if(e!=Error::Ok)return e;
    if(vers.bytes!=2)return Error::Version;
    e=r.read(header,2,vers.end);if(e!=Error::Ok)return e;
    if(header[0]!=0||header[1]!=3)return Error::Version;
    e=r.padding(vers);if(e!=Error::Ok)return e;
    while(r.at<input.bytes) {
        detail::Chunk list,bhdr,rawd,data;
        e=r.chunk("LIST",input.bytes,list);if(e!=Error::Ok)return e;
        e=r.read(header,4,list.end);if(e!=Error::Ok)return e;
        if(!detail::fourcc(header,"BUFR"))return Error::Chunk;
        e=r.chunk("BHDR",list.end,bhdr);if(e!=Error::Ok)return e;
        if(bhdr.bytes!=2)return Error::Metadata;
        e=r.read(header,2,bhdr.end);if(e!=Error::Ok)return e;
        Record record{detail::word(header),0};
        if(record.buffer_id==65535)return Error::BufferId;
        e=r.padding(bhdr);if(e!=Error::Ok)return e;
        e=r.chunk("RAWD",list.end,rawd);if(e!=Error::Ok)return e;
        if(rawd.bytes!=1)return Error::Metadata;
        e=r.read(header,1,rawd.end);if(e!=Error::Ok)return e;
        if(header[0])return Error::Metadata;
        e=r.padding(rawd);if(e!=Error::Ok)return e;
        e=r.chunk("DATA",list.end,data);if(e!=Error::Ok)return e;
        if(!data.bytes||data.bytes>0xffffffUL)return Error::DataSize;
        if(data.next!=list.end)return Error::Chunk;
        record.data_bytes=data.bytes;
        if(!detail::command(transport,record.buffer_id,2))return Error::Transport;
        uint32_t left=data.bytes;
        while(left) {
            const uint16_t n=left>sizeof workspace.data?uint16_t(sizeof workspace.data):uint16_t(left);
            e=r.read(workspace.data,n,data.end);if(e!=Error::Ok)return e;
            const uint8_t write[]={23,0,160,uint8_t(record.buffer_id),uint8_t(record.buffer_id>>8),0,uint8_t(n),uint8_t(n>>8)};
            if(!transport.send(transport.context,write,sizeof write)||
               !transport.send(transport.context,workspace.data,n))return Error::Transport;
            left-=n;
        }
        if(!detail::command(transport,record.buffer_id,14))return Error::Transport;
        e=r.padding(data);if(e!=Error::Ok)return e;
        e=r.padding(list);if(e!=Error::Ok)return e;
        if(completed)completed(callback_context,record);
    }
    return Error::Ok;
}
} // namespace agnb
