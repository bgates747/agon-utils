#include "lifecycle.h"
#include <assert.h>
#include <stdio.h>
using namespace suite;
struct Context {int starts=0, executions=0, ends=0, cleanups=0; int start_fail=0,end_fail=0,cleanup_fail=0; Result result={Outcome::Passed,1,0,""};};
bool start(void* p,const Case&) {auto& c=*static_cast<Context*>(p); return ++c.starts!=c.start_fail;}
Result execute(void* p,const Case&) {auto& c=*static_cast<Context*>(p); ++c.executions; return c.result;}
bool finish(void* p,const Case&,const Result&) {auto& c=*static_cast<Context*>(p); return ++c.ends!=c.end_fail;}
bool cleanup(void* p,const Case&) {auto& c=*static_cast<Context*>(p); return ++c.cleanups!=c.cleanup_fail;}
Totals go(Context& c,const Case*const* plan,size_t n,uint32_t caps=0) {return run(plan,n,caps,{&c,start,execute,finish,cleanup});}
int main() {
 Case a={1,"a","f","g",0}, b={2,"b","f","g",0}, u={3,"u","f","g",1};
 const Case* two[]={&a,&b}; const Case* duplicate[]={&a,&a}; const Case* conditional[]={&a,&u};
 {Context c; auto t=go(c,two,2); assert(t.complete && t.counts[0]==2 && c.executions==2 && c.cleanups==2);}
 {Context c;c.result={Outcome::Failed,2,1,"intentional"}; auto t=go(c,two,2); assert(t.complete && t.counts[1]==2 && c.executions==2);}
 {Context c;auto t=go(c,conditional,2); assert(t.complete && t.counts[4]==1 && c.executions==1 && c.cleanups==1);}
 {Context c;auto t=go(c,duplicate,2); assert(!t.complete && t.infrastructure_error && c.starts==0);}
 {Context c;auto t=go(c,two,0); assert(!t.complete && c.starts==0);}
 {Context c;c.start_fail=1;auto t=go(c,two,2); assert(!t.complete && c.executions==0 && c.ends==0);}
 {Context c;c.end_fail=1;auto t=go(c,two,2); assert(!t.complete && t.terminal==0 && c.executions==1);}
 {Context c;c.cleanup_fail=1;auto t=go(c,two,2); assert(!t.complete && t.terminal==1 && c.executions==1);}
 {Context c;c.result={Outcome::Passed,0,0,""};auto t=go(c,two,2); assert(!t.complete && t.counts[6]==1 && c.executions==1);}
 {Context c;c.result={Outcome::Incomplete,0,0,"fault"};auto t=go(c,two,2); assert(!t.complete && t.counts[7]==1 && c.executions==1);}
 {Context c;c.result={Outcome::Blocked,0,0,"capture pending"};auto t=go(c,two,2); assert(t.complete && t.counts[5]==2 && !t.counts[0]);}
 puts("PASSED: 11 lifecycle controls; native execution only, not target capture qualification.");
}
