#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "recording.h"
namespace bounded_json {
struct Node {size_t start=0,end=0;unsigned next=0;char kind=0;};
struct Document {
 const char* text=nullptr;size_t length=0,pos=0;unsigned count=0;Node nodes[1024];
 void space(){while(pos<length&&(text[pos]==' '||text[pos]=='\n'||text[pos]=='\r'||text[pos]=='\t'))++pos;}
 static int digit(char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;}
 bool string(unsigned i,char* out,size_t cap)const{
  if(i>=count||nodes[i].kind!='"'||!cap)return false;size_t p=nodes[i].start+1,n=0;
  while(p<nodes[i].end-1){unsigned char c=text[p++];
   if(c=='\\'){if(p>=nodes[i].end-1)return false;c=text[p++];
    if(c=='u'){if(p+4>nodes[i].end-1)return false;unsigned v=0;for(unsigned j=0;j<4;++j){int d=digit(text[p++]);if(d<0)return false;v=(v<<4)|d;}if(!v||v>127)return false;c=v;}
    else if(c=='n')c='\n';else if(c=='r')c='\r';else if(c=='t')c='\t';else if(c=='b')c='\b';else if(c=='f')c='\f';else if(c!='"'&&c!='\\'&&c!='/')return false;
   }
   if(!c||n+1>=cap)return false;out[n++]=c;
  }
  out[n]=0;return suite::wire::utf8(out,n);
 }
 bool value(unsigned depth=0){
  space();if(pos>=length||depth>8||count==1024)return false;
  unsigned i=count++;nodes[i].start=pos;char c=text[pos++];nodes[i].kind=c;
  if(c=='{'||c=='['){
   char closing=c=='{'?'}':']';space();
   if(pos<length&&text[pos]==closing)++pos;
   else for(;;){
    if(c=='{'){
     space();if(pos>=length||text[pos]!='"')return false;
     unsigned key=count;if(!value(depth+1))return false;char a[256],b[256];if(!string(key,a,sizeof a))return false;
     for(unsigned k=i+1;k<key;k=nodes[k+1].next){if(!string(k,b,sizeof b)||!strcmp(a,b))return false;}
     space();if(pos>=length||text[pos++]!=':')return false;
    }
    if(!value(depth+1))return false;space();if(pos>=length)return false;
    char sep=text[pos++];if(sep==closing)break;if(sep!=',')return false;
   }
  }else if(c=='"'){
   bool done=false;while(pos<length){unsigned char d=text[pos++];if(d=='"'){done=true;break;}if(d<32)return false;if(d=='\\'){if(pos>=length)return false;++pos;}}
   if(!done)return false;nodes[i].end=pos;char check[1025];if(!string(i,check,sizeof check))return false;
  }else{
   while(pos<length&&text[pos]!=','&&text[pos]!=']'&&text[pos]!='}'&&text[pos]!=' '&&text[pos]!='\r'&&text[pos]!='\n'&&text[pos]!='\t')++pos;
   size_t n=pos-nodes[i].start;const char* start=text+nodes[i].start;
   if((n==4&&!memcmp(start,"null",4))||(n==4&&!memcmp(start,"true",4))||(n==5&&!memcmp(start,"false",5))){}
   else {if(c<'0'||c>'9'||(n>1&&c=='0'))return false;for(size_t k=1;k<n;++k)if(start[k]<'0'||start[k]>'9')return false;nodes[i].kind='N';}
  }
  nodes[i].end=pos;nodes[i].next=count;return true;
 }
 bool parse(const char* data,size_t size){text=data;length=size;pos=0;count=0;if(!size||size>16384||!value())return false;space();return pos==length;}
 int get(unsigned object,const char* name)const {
  if(object>=count||nodes[object].kind!='{')return -1;char key[256];
  for(unsigned k=object+1;k<nodes[object].next;k=nodes[k+1].next)if(string(k,key,sizeof key)&&!strcmp(key,name))return k+1;
  return -1;
 }
 bool fields(unsigned object,const char* const* names,unsigned n)const{
  if(object>=count||nodes[object].kind!='{')return false;unsigned found=0;
  for(unsigned k=object+1;k<nodes[object].next;k=nodes[k+1].next)++found;
  if(found!=n)return false;for(unsigned i=0;i<n;++i)if(get(object,names[i])<0)return false;return true;
 }
 bool literal(unsigned i,const char* s)const{return i<count&&nodes[i].end-nodes[i].start==strlen(s)&&!memcmp(text+nodes[i].start,s,strlen(s));}
 static bool decimal(const char* s,uint64_t& v){v=0;if(!*s||(*s=='0'&&s[1]))return false;for(;*s;++s){if(*s<'0'||*s>'9')return false;unsigned d=*s-'0';if(v>(UINT64_MAX-d)/10)return false;v=v*10+d;}return true;}
 bool generation(unsigned i,uint64_t& v)const{char s[32];return string(i,s,sizeof s)&&decimal(s,v)&&v>0;}
};
struct Writer {
 char* data;size_t cap,used=0;bool ok=true;
 Writer(char* d,size_t c):data(d),cap(c){if(cap)data[0]=0;}
 void raw(const char* s){size_t n=strlen(s);if(!ok||n>=cap-used){ok=false;return;}memcpy(data+used,s,n);used+=n;data[used]=0;}
 void string(const char* s){raw("\"");for(;*s&&ok;++s){unsigned char c=*s;if(c=='"'||c=='\\'){char x[3]={'\\',char(c),0};raw(x);}else if(c<32){const char* h="0123456789abcdef";char x[7]={'\\','u','0','0',h[c>>4],h[c&15],0};raw(x);}else{char x[2]={char(c),0};raw(x);}}raw("\"");}
};
}
