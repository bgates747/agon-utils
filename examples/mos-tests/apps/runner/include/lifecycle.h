#pragma once
#include <stdint.h>
#include <stddef.h>
namespace suite {
enum class Outcome : uint8_t { Passed=1, Failed, Observed, Skipped, Unsupported, Blocked, Error, Incomplete };
struct Result { Outcome outcome; uint32_t assertions, failed; const char* reason; };
struct Case { uint32_t key; const char *id, *function, *group; uint32_t required; };
struct Hooks {
    void* context;
    bool (*start)(void*, const Case&);
    Result (*execute)(void*, const Case&);
    bool (*finish)(void*, const Case&, const Result&);
    bool (*cleanup)(void*, const Case&);
};
struct Totals { uint32_t counts[8]; uint32_t terminal; bool complete; bool infrastructure_error; };
inline bool valid(const Result& r) {
    unsigned n=static_cast<unsigned>(r.outcome);
    if(n<1 || n>8 || r.failed>r.assertions) return false;
    if(r.outcome==Outcome::Passed) return r.assertions>0 && r.failed==0;
    if(!r.reason || !*r.reason) return false;
    if(r.outcome==Outcome::Failed) return r.failed>0;
    if(n>=3 && n<=6) return r.assertions==0 && r.failed==0;
    return true;
}
// Hooks provide durable boundaries. No production I/O or capture is implied here.
inline Totals run(const Case* const* plan, size_t count, uint32_t capabilities, const Hooks& h) {
    Totals t={};
    if(!count || !h.start || !h.execute || !h.finish || !h.cleanup) { t.infrastructure_error=true; return t; }
    // Validate the whole plan before any effect.
    for(size_t i=0;i<count;++i) {
        if(!plan[i] || !plan[i]->key) { t.infrastructure_error=true; return t; }
        for(size_t j=0;j<i;++j) if(plan[i]->key==plan[j]->key) { t.infrastructure_error=true; return t; }
    }
    for(size_t i=0;i<count;++i) {
        const Case& c=*plan[i];
        if(!h.start(h.context,c)) { t.infrastructure_error=true; return t; }
        const bool supported=(c.required & capabilities)==c.required;
        Result r=supported ? h.execute(h.context,c) : Result{Outcome::Unsupported,0,0,"missing capability"};
        if(!valid(r)) r={Outcome::Error,0,0,"invalid executor result"};
        // Finish means evidence committed; cleanup failure still makes the run incomplete.
        if(!h.finish(h.context,c,r)) { t.infrastructure_error=true; return t; }
        ++t.counts[static_cast<unsigned>(r.outcome)-1]; ++t.terminal;
        if(supported && !h.cleanup(h.context,c)) { t.infrastructure_error=true; return t; }
        if(r.outcome==Outcome::Error || r.outcome==Outcome::Incomplete) { t.infrastructure_error=true; return t; }
    }
    t.complete=true; return t;
}
}
