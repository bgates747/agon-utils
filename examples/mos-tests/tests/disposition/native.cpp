#include "bounded_json.h"
#include <cassert>
#include <cstdio>
#include <string>
using namespace bounded_json;
int main(){
 Document d;std::string backing;auto parse=[&](const std::string&s){backing=s;return d.parse(backing.data(),backing.size());};
 assert(parse("{\"a\":1,\"b\":[true,null,\"ok\"]}"));const char* fields[]={"a","b"};assert(d.fields(0,fields,2));assert(!d.fields(0,fields,1));
 for(const char* s:{"{\"a\":1,\"a\":2}","{\"a\":1,\"\\u0061\":2}","{\"a\":}","[1,]","{\"a\":1,}","01","-1","1.1","true false","\"\\u0000\"","\"\\x\"","\"\\u00ff\"","\"\xc0\x80\""})assert(!parse(s));
 assert(!parse(std::string(16385,' ')));assert(!parse("[[[[[[[[[[0]]]]]]]]]]"));
 std::string many="[";for(int i=0;i<1024;i++){if(i)many+=",";many+="0";}many+="]";assert(!parse(many));
 uint64_t n;assert(Document::decimal("18446744073709551615",n)&&n==UINT64_MAX);assert(!Document::decimal("18446744073709551616",n));assert(!Document::decimal("01",n));
 const char* value="line\nquoted \"text\" \\ café";char b[256],decoded[256];Writer w(b,sizeof b);w.string(value);assert(w.ok&&parse(b)&&d.string(0,decoded,sizeof decoded)&&!strcmp(value,decoded));
 char tiny[3];Writer small(tiny,sizeof tiny);small.string("long");assert(!small.ok);
 // Every byte truncation of this complete container must fail.
 std::string complete="{\"schema\":1,\"actor\":\"human\",\"case_ids\":[\"a\",\"b\"]}";
 for(size_t i=0;i<complete.size();++i)assert(!d.parse(complete.data(),i));
 puts("PASSED: bounded JSON structural, duplicate, UTF-8, overflow, truncation and writer controls.");
}
