"""CLI contract tests use real temp outputs; they do not execute MOS cases."""
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
script=ROOT/'scripts/plan_run.py'
def invoke(*args):return subprocess.run([sys.executable,str(script),*map(str,args)],capture_output=True,text=True)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp); out=root/'run'
 r=invoke('--output',out,'--backend','emulator','function:synthetic_preserve','group:controls')
 assert r.returncode==0,r.stderr
 plan=json.loads((out/'plan.json').read_text()); assert plan['case_keys']==[1,2,3]
 assert json.loads((out/'planning.json').read_text())['state']=='PLANNED — NOT EXECUTED'
 original=(out/'plan.json').read_bytes()
 assert invoke('--output',out,'--backend','emulator','all').returncode!=0
 assert (out/'plan.json').read_bytes()==original
 for name,args in [('unknown',['typo']),('empty',[]),('bad-cap',['--capability','imaginary','all'])]:
  dest=root/name;r=invoke('--output',dest,'--backend','emulator',*args)
  assert r.returncode!=0 and not dest.exists(),(name,r.stdout,r.stderr)
 dest=root/'single';assert invoke('--output',dest,'--backend','hardware','case:control.ix-upper.001').returncode==0
 assert json.loads((dest/'plan.json').read_text())['case_keys']==[2]
 print('PASSED: planner stable union, exact selection, explicit backend, collision preservation and pre-output rejection checks.')
