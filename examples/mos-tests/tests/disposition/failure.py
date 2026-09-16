"""A retry must not erase or absorb a confirmed parent failure."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from startup_bundle import build,script_text
from run_startup import run
from recovery_action import prepare,apply
def check(out):
 out.mkdir(parents=True,exist_ok=False)
 script=out/'autoexec.txt';script.write_text(script_text(['synthetic_preserve','synthetic_clobber']))
 bundle=build(out/'bundle',script,fault=1)
 prior=run(bundle,out/'parent',stop_after=2)
 assert prior['reports'][0]['report']['failed_tests']==1
 slot=max([(out/'parent'/n).read_bytes() for n in ['recovery-a.bin','recovery-b.bin']],key=lambda b:int.from_bytes(b[16:24],'little'))
 subject=slot[24:40].hex();generation=int.from_bytes(slot[16:24],'little')
 req=prepare(out/'request','retry',subject,generation,['control.ix-upper.001'],'qualification','Retain confirmed failure; explicitly run the other case.',True)
 result=apply(bundle,req,out/'action');assert result['accepted']
 assert result['execution']['recovery_gate']['journal_generation']==str(generation+2)
 child=run(bundle,out/'child');assert child['command_statuses']==[0]*3
 assert child['reports'][0]['report']['failed_tests']==1 and child['reports'][0]['report']['verdict']!='ALL TESTS PASSED'
 assert child['reports'][-1]['report']['verdict']=='ALL TESTS PASSED' and child['reports'][-1]['report']['counts']['PASSED']==1
 def snapshot(folder):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
 assert snapshot(out/'parent/runs'/subject)==snapshot(out/'child/runs'/subject)
 (out/'result.json').write_text(json.dumps({'passed':True,'parent_failure_count':1,'child_pass_count':1,'hardware_tested':False},indent=2)+'\n')
 print('PASSED: child pass preserves confirmed parent failure and original bytes.',flush=True)
if __name__=='__main__':check(Path(sys.argv[1]).resolve())
