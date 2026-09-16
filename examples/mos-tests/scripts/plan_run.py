"""Persist a validated plan; does not execute tests. Shared selection is C++."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,uuid
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'catalogue/catalogue.json'
CAPS={'capture.primary':1,'uart.peer':2}
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pairs(items):
    result={}
    for k,v in items:
        if k in result: raise ValueError('duplicate JSON key: '+k)
        result[k]=v
    return result

def catalogue():
    obj=json.loads(CAT.read_text(),object_pairs_hook=pairs)
    if set(obj)!={'schema','cases'} or obj['schema']!=1 or not obj['cases']: raise ValueError('invalid catalogue')
    keys=set(); ids=set()
    fields={'key','id','function','route','group','expectation_sha256','fixture_sha256','capabilities','isolation','samples','timeout_ms'}
    available={digest(f) for f in (ROOT/'fixtures/synthetic').glob('*.json')}
    for c in obj['cases']:
        if set(c)!=fields: raise ValueError('invalid case fields')
        if type(c['key']) is not int or not 0<c['key']<=0xffffffff or c['key'] in keys: raise ValueError('duplicate/invalid case key')
        if c['id'] in ids: raise ValueError('duplicate ID')
        for field in ('id','function','group'):
            if not isinstance(c[field],str) or not re.fullmatch(r'[A-Za-z0-9._-]+',c[field]): raise ValueError('invalid identifier')
        if c['route']!='synthetic' or c['isolation']!='pure': raise ValueError('unsupported foundation route/isolation')
        if len(set(c['capabilities']))!=len(c['capabilities']) or any(x not in CAPS for x in c['capabilities']): raise ValueError('invalid capabilities')
        if not c['samples'] or len(set(c['samples']))!=len(c['samples']) or any(type(x)is not int or not 0<=x<=65535 for x in c['samples']): raise ValueError('invalid samples')
        if type(c['timeout_ms'])is not int or not 0<c['timeout_ms']<=0xffffffff: raise ValueError('invalid timeout')
        if any(c[x] not in available for x in ['expectation_sha256','fixture_sha256']): raise ValueError('missing fixture/expectation identity')
        keys.add(c['key']); ids.add(c['id'])
    return obj

def prepare():
    cat=catalogue(); folder=ROOT/'apps/runner'; build=folder/'build'; build.mkdir(exist_ok=True)
    lines=['// Generated from catalogue/catalogue.json; do not edit.','#pragma once','#include "lifecycle.h"','static const char CATALOGUE_SHA256[]="'+digest(CAT)+'";','static const suite::Case CASES[]={']
    for c in cat['cases']:
        mask=sum(CAPS[x] for x in c['capabilities'])
        lines.append('{%d,"%s","%s","%s",%d},'%(c['key'],c['id'],c['function'],c['group'],mask))
    lines+=['};','static constexpr size_t CASE_COUNT=sizeof(CASES)/sizeof(CASES[0]);']
    header=folder/'include/catalogue_generated.h'; data='\n'.join(lines)+'\n'
    if not header.exists() or header.read_text()!=data: header.write_text(data)
    binary=build/'selector'
    inputs=[folder/'src/main.cpp',header,folder/'include/lifecycle.h']
    if not binary.exists() or any(f.stat().st_mtime>binary.stat().st_mtime for f in inputs):
        subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-I'+str(folder/'include'),str(inputs[0]),'-o',str(binary)],check=True)
    return cat,binary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list',action='store_true'); ap.add_argument('--output',type=Path)
    ap.add_argument('--backend',choices=['emulator','hardware']); ap.add_argument('--capability',action='append',default=[])
    ap.add_argument('--script',type=Path,help='Optional existing selection script identity; parsing is W06')
    ap.add_argument('selectors',nargs='*')
    a=ap.parse_args()
    cat,binary=prepare()
    if a.list:
        if a.output or a.selectors: ap.error('--list cannot create a run')
        subprocess.run([str(binary),'--list'],check=True); return
    if not a.output or not a.backend or not a.selectors: ap.error('planning requires --output, --backend and selectors')
    if len(set(a.capability))!=len(a.capability) or any(x not in CAPS for x in a.capability): ap.error('unknown/duplicate capability')
    r=subprocess.run([str(binary),'--resolve',*a.selectors],capture_output=True,text=True)
    if r.returncode: ap.error(r.stderr.strip())
    keys=[int(x) for x in r.stdout.splitlines()]
    if not keys: ap.error('empty selection')
    # Until W06, explicit CLI selection owns the plan; empty script bytes are hashed.
    script=a.script.read_bytes() if a.script else b''
    plan={'schema':1,'catalogue_sha256':digest(CAT),'selectors':a.selectors,'case_keys':keys,'backend':a.backend,'capabilities':a.capability,'script_sha256':hashlib.sha256(script).hexdigest()}
    target=a.output.resolve(); target.mkdir(parents=True,exist_ok=False)
    (target/'catalogue.json').write_bytes(CAT.read_bytes()); (target/'selection-script.txt').write_bytes(script)
    (target/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    statuses=[{'key':c['key'],'id':c['id'],'state':'planned','missing_capabilities':[x for x in c['capabilities'] if x not in a.capability]} for c in cat['cases'] if c['key'] in keys]
    (target/'planning.json').write_text(json.dumps({'planning_id':uuid.uuid4().hex,'plan_sha256':digest(target/'plan.json'),'state':'PLANNED — NOT EXECUTED','cases':statuses},indent=2)+'\n')
    print('PLANNED — NOT EXECUTED: %d selected cases. Saved %s'%(len(keys),target))
if __name__=='__main__': main()
