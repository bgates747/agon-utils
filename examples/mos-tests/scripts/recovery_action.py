"""Prepare explicit recovery requests; optionally apply through the target helper."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from startup_bundle import script_text
from run_startup import run
def prepare(out,action,subject,generation,cases,actor,reason,prerequisites):
    if action not in {'park','retry','continue'}:raise ValueError('unknown action')
    if not re.fullmatch('[0-9a-f]{32}',subject) or int(subject,16)==0:raise ValueError('subject must be a nonzero 32-digit lowercase run ID')
    if not 0<int(generation)<2**64:raise ValueError('invalid expected journal generation')
    if not actor or not reason:raise ValueError('actor and reason are required')
    if len(actor.encode())>128 or len(reason.encode())>512:raise ValueError('actor/reason exceeds target bounds')
    catalogue=json.loads((ROOT/'catalogue/catalogue.json').read_text())['cases']
    ids=[c['id'] for c in catalogue]
    if len(set(cases))!=len(cases) or any(c not in ids for c in cases):raise ValueError('duplicate/unknown selected case')
    if '\x00' in actor or '\x00' in reason:raise ValueError('actor/reason must not contain NUL')
    selected=[c for c in catalogue if c['id'] in cases]
    if [c['id'] for c in selected]!=cases:raise ValueError('select cases in catalogue order')
    if action=='park':
        if cases:raise ValueError('park takes no case selection')
        digest=None
        out.mkdir(parents=True,exist_ok=False)
    else:
        if not cases or not prerequisites:raise ValueError('retry/continue requires explicit cases and --prerequisites-confirmed')
        out.mkdir(parents=True,exist_ok=False)
        text=script_text([c['function'] for c in selected]).encode();(out/'autoexec.txt').write_bytes(text);digest=hashlib.sha256(text).hexdigest()
    request={'schema':1,'subject_run_id':subject,'journal_generation':str(generation),'action':action,'case_ids':cases,'script_sha256':digest,'actor':actor,'reason':reason,'prerequisites_confirmed':bool(prerequisites)}
    (out/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
    return out
def apply(bundle,prepared,out,stop_symbol=None):
    out.mkdir(parents=True,exist_ok=False)
    image=bundle/'sd.img';mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy'
    def copy(source,dest):
        subprocess.run([str(mcopy),'-o','-i',str(image)+'@@1048576',str(source),str(dest)],check=True)
    original=out/'original-boot.obey';copy('::/!boot.obey',original)
    copy(prepared/'request.json','::/mos-tests/request.json')
    if (prepared/'autoexec.txt').exists():copy(prepared/'autoexec.txt','::/autoexec.txt')
    script=out/'recovery.obey';script.write_text('LOAD /mos-tests/runner.bin\nRUN . recover\n');copy(script,'::/recovery.obey')
    boot=out/'recovery-boot.obey';boot.write_text('SET KEYBOARD 1\nEXEC /recovery.obey\n')
    try:
        copy(boot,'::/!boot.obey')
        result=run(bundle,out/'execution',stop_symbol=stop_symbol)
    finally:
        # A killed host may leave this boot script in place; expected generation
        # prevents stale request replay. Never delete disposition evidence.
        copy(original,'::/!boot.obey')
    request=json.loads((prepared/'request.json').read_text())
    success=result['command_statuses']==[0] and result['returned_to_mos_prompt'] and result['recovery_gate']['phase']==(9 if request['action']=='park' else 10)
    receipt={'accepted':success,'request':request,'execution':result}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--bundle',type=Path,help='apply on an existing emulator image; omit to prepare files only')
    ap.add_argument('--action',required=True,choices=['park','retry','continue']);ap.add_argument('--run-id',required=True);ap.add_argument('--generation',required=True,type=int)
    ap.add_argument('--case',action='append',default=[]);ap.add_argument('--actor',required=True);ap.add_argument('--reason',required=True);ap.add_argument('--prerequisites-confirmed',action='store_true');a=ap.parse_args()
    out=a.output.resolve()
    if a.bundle:
        out.mkdir(parents=True,exist_ok=False)
        prepared=prepare(out/'prepared',a.action,a.run_id,a.generation,a.case,a.actor,a.reason,a.prerequisites_confirmed)
        receipt=apply(a.bundle.resolve(),prepared,out/'applied')
        print(('PARKED' if a.action=='park' else 'ARMED')+': explicit recovery disposition accepted; original evidence retained.' if receipt['accepted'] else 'INCOMPLETE: disposition was not accepted; inspect saved evidence.')
        return 0 if receipt['accepted'] else 2
    prepare(out,a.action,a.run_id,a.generation,a.case,a.actor,a.reason,a.prerequisites_confirmed)
    print('PREPARED: request files only; no target action or authorization consumed.')
    return 0
if __name__=='__main__':sys.exit(main())
