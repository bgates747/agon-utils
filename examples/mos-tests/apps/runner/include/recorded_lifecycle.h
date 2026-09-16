#pragma once
#include "lifecycle.h"
#include "recording.h"
namespace suite {
// Metadata/execution remain caller-owned; this bridge supplies durable boundaries.
struct RecordedLifecycle {
 Recorder& recorder;void* context;
 bool (*metadata)(void*,const Case&,wire::Payload&);
 Result (*execute_case)(void*,const Case&);
 bool (*cleanup_case)(void*,const Case&);
 uint32_t observations=0;
 RecordedLifecycle(Recorder& r,void* c,bool (*m)(void*,const Case&,wire::Payload&),Result (*e)(void*,const Case&),bool (*clean)(void*,const Case&)):
  recorder(r),context(c),metadata(m),execute_case(e),cleanup_case(clean){}
 bool observation(const wire::Payload& p) {
  if(p.size<16||p.bytes[6]||p.bytes[7]||p.bytes[8]!=1||p.bytes[9])return false;
  if(observations==UINT32_MAX)return recorder.fail(5,5,recorder.next);
  if(!recorder.current||!recorder.append(3,p)||!recorder.checkpoint())return false;
  // Call for completed logical observations only (v1 first integration: one chunk).
  ++observations;return true;
 }
 static bool start(void* ptr,const Case& c) {
  auto& s=*static_cast<RecordedLifecycle*>(ptr);wire::Payload p;s.observations=0;
  return s.metadata(s.context,c,p)&&s.recorder.start_case(c.key,p);
 }
 static Result execute(void* ptr,const Case& c) {auto& s=*static_cast<RecordedLifecycle*>(ptr);return s.execute_case(s.context,c);}
 static bool finish(void* ptr,const Case&,const Result& r) {
  auto& s=*static_cast<RecordedLifecycle*>(ptr);wire::Payload p;
  return p.case_end(static_cast<uint8_t>(r.outcome),r.assertions,r.failed,s.observations,r.reason?r.reason:"")&&s.recorder.finish_case(p);
 }
 static bool cleanup(void* ptr,const Case& c) {auto& s=*static_cast<RecordedLifecycle*>(ptr);return s.cleanup_case(s.context,c);}
 Hooks hooks() {return {this,start,execute,finish,cleanup};}
};
}
