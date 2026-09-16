"""Explicit recovery qualification on headless raw SD images."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from startup_bundle import build,script_text
from run_startup import run
from recovery_action import prepare,apply
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}
def latest(p):return max([(p/n).read_bytes() for n in ['recovery-a.bin','recovery-b.bin']],key=lambda b:int.from_bytes(b[16:24],'little'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);checks=[]
 def passed(name):checks.append(name);print('PASSED: '+name,flush=True)
 native=out/'native'
 subprocess.run(['g++','-std=c++14','-fsanitize=address,undefined','-g','-I'+str(ROOT/'apps/startup-runner/include'),'-I'+str(ROOT/'apps/runner/include'),str(ROOT/'tests/disposition/native.cpp'),'-o',str(native)],check=True)
 subprocess.run([str(native)],check=True);passed('bounded JSON parser/writer')
 script=out/'autoexec.txt';script.write_text(script_text(['synthetic_preserve','synthetic_clobber']))
 fresh=build(out/'fresh',script)
 def clone(src,name):dest=out/(name+'-bundle');shutil.copytree(src,dest);return dest
 interrupted=clone(fresh,'interrupted');run(interrupted,out/'parent',stop_after=2)
 parent=out/'parent';slot=latest(parent);subject=slot[24:40].hex();generation=int.from_bytes(slot[16:24],'little');original=snapshot(parent/'runs')
 mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy'
 def put(bundle,path,data):
  source=out/'mutation.bin';source.write_bytes(data)
  subprocess.run([str(mcopy),'-o','-i',str(bundle/'sd.img')+'@@1048576',str(source),'::/'+path],check=True)
 def unchanged(folder):
  assert snapshot(folder/'runs')==original
 def request(name,action='park',gen=generation,cases=()):
  return prepare(out/(name+'-request'),action,subject,gen,list(cases),'qualification','Explicit synthetic recovery control.',action!='park')
 def action(bundle,name,req,stop=None):
  r=apply(bundle,req,out/name,stop_symbol=stop)
  return r,out/name/'execution'
 def boot(bundle,name,blocked=False,stop=None):
  r=run(bundle,out/name,stop_symbol=stop)
  if blocked:assert r['command_statuses']==[41],(name,r)
  return r,out/name
 # Rejection must leave journal and original evidence byte-for-byte unchanged.
 for name,edit in [
  ('stale-generation',lambda d:d.update(journal_generation=str(generation-1))),
  ('wrong-subject',lambda d:d.update(subject_run_id=subject[:16]+'0200000000000000')),
  ('missing-prerequisites',lambda d:d.update(prerequisites_confirmed=False)),
  ('wrong-script',lambda d:d.update(script_sha256='ab'*32)),
  ('unknown-field',lambda d:d.update(unexpected=True)),
  ('duplicate-field',None),
  ('continue-completed',lambda d:None)]:
  bundle=clone(interrupted,name);req=request(name,'continue' if name=='continue-completed' else 'retry',cases=['control.preserve.001'])
  d=json.loads((req/'request.json').read_text())
  if edit:edit(d);(req/'request.json').write_text(json.dumps(d)+'\n')
  else:(req/'request.json').write_text(json.dumps(d)[:-1]+', "schema": 1}\n')
  r,folder=action(bundle,name,req);assert not r['accepted'] and r['execution']['command_statuses']==[44],(name,r)
  unchanged(folder)
  for n in ['recovery-a.bin','recovery-b.bin','install.bin']:assert (folder/n).read_bytes()==(parent/n).read_bytes()
  passed(name+' rejected without evidence mutation')
 # Park remains stopped; explicit continuation authorizes only the remaining case.
 bundle=clone(interrupted,'park');req=request('park');r,folder=action(bundle,'park',req);assert r['accepted'];unchanged(folder)
 parked=clone(bundle,'parked-snapshot')
 for name in ['parked-boot','parked-again']:
  r,p=boot(bundle,name,True);unchanged(p)
 passed('park and repeated stopped boots preserve parent')
 req=request('continuation','continue',int.from_bytes(latest(folder)[16:24],'little'),['control.ix-upper.001'])
 r,armed=action(bundle,'continuation',req);assert r['accepted'];unchanged(armed)
 armed_bundle=clone(bundle,'armed-snapshot')
 r,child=boot(bundle,'child');assert r['command_statuses']==[0]*3
 assert [(x['report']['verdict']) for x in r['reports']]==['INCOMPLETE','ALL TESTS PASSED']
 childid=next(p.name for p in (child/'runs').iterdir() if p.name!=subject)
 manifest=json.loads((child/'runs'/childid/'run.json').read_text())
 assert manifest['schema']==2 and manifest['parent_run_id']==subject
 assert r['reports'][-1]['report']['counts']['PASSED']==1
 assert snapshot(child/'runs'/subject)==snapshot(parent/'runs'/subject)
 # Host schema2 rejects a removed receipt and a modified child parent.
 for name,mutate in [('child-missing-receipt',lambda d:(d/'disposition.json').unlink()),('child-wrong-parent',lambda d:(d/'run.json').write_text((d/'run.json').read_text().replace(subject,'0'*32)))]:
  dest=out/name;shutil.copytree(child/'runs'/childid,dest);mutate(dest)
  p=subprocess.run([sys.executable,str(ROOT/'scripts/report_results.py'),'--run',str(dest),'--output',str(out/(name+'-report'))],capture_output=True,text=True)
  assert p.returncode!=0 and json.loads((out/(name+'-report')/'report.json').read_text())['verdict']!='ALL TESTS PASSED'
 passed('selected child schema2 and independent parent verdict; malformed child rejected')
 r,repeat=boot(bundle,'ordinary-after-child');assert r['command_statuses']==[0]*3 and len(r['reports'])==3
 assert json.loads((repeat/'runs'/r['reports'][-1]['run']/'run.json').read_text())['schema']==1
 passed('completed child permits ordinary subsequent boot')
 # Replay cannot consume an old authorization twice.
 r,p=action(bundle,'consumed-request',req);assert not r['accepted'] and r['execution']['command_statuses']==[44]
 passed('consumed stale request rejected')
 # Retry may explicitly select a case already completed in its parent.
 retry=clone(interrupted,'retry');req=request('retry','retry',cases=['control.preserve.001'])
 r,p=action(retry,'retry',req);assert r['accepted']
 r,p=boot(retry,'retry-child');assert r['command_statuses']==[0]*3 and r['reports'][-1]['report']['verdict']=='ALL TESTS PASSED'
 assert r['reports'][-1]['run']!=subject;passed('explicit retry creates fresh linked child')
 for name,suffix in [('receipt-tamper','.json'),('certificate-tamper','.accepted')]:
  b=clone(armed_bundle,name);f=next((armed/'recovery').glob('*'+suffix));data=bytearray(f.read_bytes());data[-1]^=1;put(b,'mos-tests/recovery/'+f.name,data)
  r,p=boot(b,name,True);unchanged(p);passed(name+' blocks execution')
 # Stop after receipt durability and after ARMED publication but before its certificate.
 for name,symbol in [('receipt-stop','_recovery_receipt_written'),('terminal-stop','_recovery_terminal')]:
  b=clone(interrupted,name);req=request(name,'retry',cases=['control.preserve.001'])
  r,p=action(b,name,req,symbol);assert not r['accepted'];unchanged(p);saved=snapshot(p/'recovery')
  boot(b,name+'-blocked',True)
  freshreq=request(name+'-fresh','retry',int.from_bytes(latest(p)[16:24],'little'),['control.preserve.001'])
  r,q=action(b,name+'-fresh',freshreq);assert r['accepted'],r
  assert all(snapshot(q/'recovery')[k]==v for k,v in saved.items())
  r,q=boot(b,name+'-child');assert r['command_statuses']==[0]*3
  passed(name+' requires fresh explicit disposition and retains orphan evidence')
 b=clone(armed_bundle,'allocation-stop');r,p=boot(b,'allocation-stop',stop='_recovery_child_allocating')
 assert latest(p)[120]==1
 r,q=boot(b,'allocation-stop-blocked',True);unchanged(q)
 assert (q/'install.bin').read_bytes()==(p/'install.bin').read_bytes()
 passed('child ALLOCATING consumes authorization before counter mutation')
 from failure import check as failure_check
 failure_check(out/'failed-parent')
 passed('confirmed parent failure retained separately from passing child')
 (out/'result.json').write_text(json.dumps({'passed':True,'checks':checks,'hardware_tested':False,'interruption':'debugger process stop and next boot; no power-loss claim'},indent=2)+'\n')
 print('PASSED: explicit disposition qualification.',flush=True)
if __name__=='__main__':main()
