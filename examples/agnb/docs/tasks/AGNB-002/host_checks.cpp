#include "../../../api/agnb_stdio.hpp"
#include <cassert>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>
using Bytes=std::vector<uint8_t>;
using agnb::Error;
struct Fixture {
    Bytes input,wire;
    size_t at=0,read_max=0,read_fail=SIZE_MAX,send_calls=0,send_fail=SIZE_MAX;
    Error read_error=Error::Read;
    std::vector<agnb::Record> completed;
    static Error read(void *p,uint8_t *out,uint16_t n){
        auto &f=*static_cast<Fixture*>(p);f.read_max=std::max(f.read_max,size_t(n));
        if(f.at+n>f.read_fail)return f.read_error;
        if(f.at+n>f.input.size())return Error::Eof;
        std::memcpy(out,f.input.data()+f.at,n);f.at+=n;return Error::Ok;
    }
    static bool send(void *p,const uint8_t *bytes,uint16_t n){
        auto &f=*static_cast<Fixture*>(p);if(f.send_calls++==f.send_fail)return false;
        f.wire.insert(f.wire.end(),bytes,bytes+n);return true;
    }
    static void done(void *p,const agnb::Record &r){static_cast<Fixture*>(p)->completed.push_back(r);}
    Error load(){agnb::Workspace workspace;return agnb::load_buffers({this,read,uint32_t(input.size())},{this,send},workspace,done,this);}
};
Bytes file(const std::string &path){std::ifstream s(path,std::ios::binary);assert(s);return Bytes(std::istreambuf_iterator<char>(s),{});}
std::map<unsigned,Bytes> decode(const Bytes &wire){
    std::map<unsigned,Bytes> buffers;size_t at=0;
    while(at<wire.size()){
        assert(at+6<=wire.size()&&wire[at]==23&&wire[at+1]==0&&wire[at+2]==160);
        unsigned id=wire[at+3]+256*wire[at+4],op=wire[at+5];at+=6;
        if(op==2)buffers.erase(id);
        else if(op==14)assert(buffers.count(id));
        else{assert(op==0&&at+2<=wire.size());unsigned n=wire[at]+256*wire[at+1];at+=2;assert(n&&at+n<=wire.size());auto &b=buffers[id];b.insert(b.end(),wire.begin()+at,wire.begin()+at+n);at+=n;}
    }
    return buffers;
}
int main(int argc,char **argv){
    assert(argc==2);std::string directory=argv[1];
    Fixture good;good.input=file(directory+"/large.agnb");assert(good.load()==Error::Ok);
    assert(good.input.size()>0x70000 && good.read_max==8192 && sizeof(agnb::Workspace)==8192);
    const std::vector<unsigned> sizes{1,8191,8192,8193,65535,65536,160000,200000};
    auto buffers=decode(good.wire);assert(buffers.size()==sizes.size()&&good.completed.size()==sizes.size());
    for(unsigned i=0;i<sizes.size();++i){assert(buffers.at(i)==Bytes(sizes[i],uint8_t(17+i)));assert(good.completed[i].buffer_id==i&&good.completed[i].data_bytes==sizes[i]);}
    unsigned cases=1;
    for(const char *name:{"id","raw","version","order","bounds","size","pad","truncated","trailing","vers-pad","bhdr-size","riff-overflow"}){
        Fixture bad;bad.input=file(directory+"/"+name+".agnb");assert(bad.load()!=Error::Ok);assert(bad.completed.empty());
        if(std::string(name)!="pad")assert(bad.wire.empty());
        ++cases;
    }
    Fixture late;late.input=file(directory+"/late.agnb");assert(late.load()==Error::Metadata);
    assert(late.completed.size()==1&&decode(late.wire).at(12)==Bytes(7,'Z'));++cases;
    Fixture duplicate;duplicate.input=file(directory+"/duplicate.agnb");assert(duplicate.load()==Error::Ok);
    assert(duplicate.completed.size()==2&&decode(duplicate.wire).at(12)==Bytes(5,'Q'));++cases;
    Fixture io;io.input=good.input;io.read_fail=128;assert(io.load()==Error::Read&&io.completed.size()==1);++cases;
    Fixture short_read;short_read.input=good.input;short_read.read_fail=128;short_read.read_error=Error::Eof;
    assert(short_read.load()==Error::Eof&&short_read.completed.size()==1);++cases;
    Fixture blocked;blocked.input=good.input;blocked.send_fail=4;assert(blocked.load()==Error::Transport&&blocked.completed.size()==1);++cases;
    agnb::Workspace workspace;Fixture stdio;
    assert(agnb::load_buffers_file((directory+"/large.agnb").c_str(),{&stdio,Fixture::send},workspace)==Error::Ok);
    assert(stdio.wire==good.wire);++cases;
    assert(agnb::load_buffers_file((directory+"/absent.agnb").c_str(),{&stdio,Fixture::send},workspace)==Error::Open);++cases;
    std::cout<<cases<<" C++ AGNB format, bounded transfer, callback and failure checks pass.\n";
}
