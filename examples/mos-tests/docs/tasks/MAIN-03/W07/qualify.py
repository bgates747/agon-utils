"""W07 aggregate replay of maintained checks; run from the subproject root."""
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path.cwd(); OUT=ROOT/'.emulator/qualification/w07-01'
PYTHON='/home/smith/Agon/mystuff/agon-utils/.venv/bin/python'
OUT.mkdir(parents=True,exist_ok=False)
def hashes(paths):
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
prior=hashes((ROOT/'.emulator/startup/qualification-03').rglob('results.bin'))
assert prior,'expected earlier W06 results'
(OUT/'prior-results-before.json').write_text(json.dumps(prior,indent=2))
steps=[]
def run(name,args):
 start=time.monotonic()
 with (OUT/(name+'.log')).open('w') as log:
  result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=args,exit_code=result.returncode,seconds=round(time.monotonic()-start,3)))
 (OUT/'steps.json').write_text(json.dumps(steps,indent=2))
 print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit('FAILED: '+name)
run('python-baseline',[PYTHON,str(ROOT/'../../tests/test_agonutils.py')])
run('planner',[PYTHON,'tests/runner/check_planner.py'])
run('lifecycle-build',['g++','-std=c++14','-Wall','-Wextra','-Werror','-Iapps/runner/include','tests/runner/lifecycle_test.cpp','-o',str(OUT/'lifecycle')])
run('lifecycle',[str(OUT/'lifecycle')])
run('runner-build',['./human/mos-tests','runner-build'])
for check in ['capture','recording','report','startup']:
 run(check,['./human/mos-tests',check+'-check','--output',str(OUT/check)])
run('smoke',['./human/mos-tests','smoke','--output',str(OUT/'smoke')])
script=OUT/'autoexec.txt'
script.write_text('LOAD /mos-tests/runner.bin\nRUN . begin\nLOAD /mos-tests/runner.bin\nRUN . function synthetic_preserve\nLOAD /mos-tests/runner.bin\nRUN . function synthetic_clobber\nLOAD /mos-tests/runner.bin\nRUN . finalize\n')
run('fresh-bundle',['./human/mos-tests','bundle','--script',str(script),'--output',str(OUT/'fresh-bundle')])
run('fresh-run',['./human/mos-tests','startup','--bundle',str(OUT/'fresh-bundle'),'--output',str(OUT/'fresh-run')])
assert prior==hashes(ROOT/p for p in prior),'previous evidence changed'
result=json.loads((OUT/'fresh-run/result.json').read_text())
assert result['returned_to_mos_prompt'] and result['command_statuses']==[0]*4
assert len(result['reports'])==1 and result['reports'][0]['report']['verdict']=='ALL TESTS PASSED'
assert result['reports'][0]['report']['counts']['PASSED']==2
ps=subprocess.check_output(['ps','-eo','pid,args'],text=True)
owned=[line for line in ps.splitlines() if 'fab-agon-emulator' in line and str(OUT) in line]
assert not owned,owned
(OUT/'result.json').write_text(json.dumps(dict(passed=True,steps=steps,prior_result_files_preserved=len(prior),owned_emulator_processes_remaining=owned,hardware_tested=False),indent=2)+'\n')
print('PASSED: W07 aggregate and independent fresh-image repeat',flush=True)
