from pathlib import Path
import sys,json
root=Path.cwd();sys.path[:0]=[str(root/'scripts'),str(root/'agents')]
from startup_bundle import build,script_text
from run_startup import run
from recovery_action import prepare,apply
out=root/'.emulator/disposition/trial-02';out.mkdir(parents=True)
script=out/'autoexec.txt';script.write_text(script_text(['synthetic_preserve','synthetic_clobber']))
bundle=build(out/'bundle',script)
r=run(bundle,out/'stopped',stop_after=2)
slots=[(out/'stopped'/n).read_bytes() for n in ['recovery-a.bin','recovery-b.bin']]
latest=max(slots,key=lambda b:int.from_bytes(b[16:24],'little'));subject=latest[24:40].hex();gen=int.from_bytes(latest[16:24],'little')
request=prepare(out/'park','park',subject,gen,[],'qualification','Preserve interruption before resuming.',False)
result=apply(bundle,request,out/'park-run');print(json.dumps({'accepted':result['accepted'],'gate':result['execution']['recovery_gate'],'statuses':result['execution']['command_statuses']},indent=2))
assert result['accepted']
again=run(bundle,out/'parked-boot');assert again['command_statuses']==[41]
slots=[(out/'park-run/execution'/n).read_bytes() for n in ['recovery-a.bin','recovery-b.bin']];latest=max(slots,key=lambda b:int.from_bytes(b[16:24],'little'))
request=prepare(out/'continue','continue',subject,int.from_bytes(latest[16:24],'little'),['control.ix-upper.001'],'qualification','Continue the explicit unexecuted case.',True)
result=apply(bundle,request,out/'continue-run');print('armed',result['accepted']);assert result['accepted']
child=run(bundle,out/'child');print(json.dumps({'statuses':child['command_statuses'],'reports':[(r['run'],r['report']['verdict']) for r in child['reports']]},indent=2))
assert child['command_statuses']==[0]*3
assert child['reports'][-1]['report']['verdict']=='ALL TESTS PASSED'
