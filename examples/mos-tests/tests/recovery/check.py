"""W02 gate checks: native wire controls and real raw-image repeat/block behavior."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from startup_bundle import build,script_text
from run_startup import run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 native=out/'native'
 subprocess.run(['g++','-std=c++14','-fsanitize=address,undefined','-g','-I'+str(ROOT/'apps/startup-runner/include'),'-I'+str(ROOT/'apps/runner/include'),str(ROOT/'tests/recovery/native.cpp'),'-o',str(native)],check=True)
 subprocess.run([str(native),str(ROOT/'fixtures/recovery-v1/idle-slot-b.bin')],check=True)
 selected=out/'selection.txt';selected.write_text(script_text(['synthetic_preserve','synthetic_clobber']))
 bundle=build(out/'clean-bundle',selected)
 first=run(bundle,out/'clean');assert first['command_statuses']==[0]*4 and first['recovery_gate']['code']==0
 assert first['reports'][0]['report']['verdict']=='ALL TESTS PASSED'
 second=run(bundle,out/'repeat');assert second['command_statuses']==[0]*4 and len(second['reports'])==2
 first_dir=next((out/'clean/runs').iterdir());again=out/'repeat/runs'/first_dir.name
 assert {f.name:sha(f) for f in first_dir.iterdir()}=={f.name:sha(f) for f in again.iterdir()}
 print('PASSED: clean and repeated boot preserve prior run',flush=True)
 # Compare native strict supported-profile records with production report evidence.
 folder=next((out/'clean/runs').iterdir());manifest=json.loads((folder/'run.json').read_text());catalogue=json.loads((folder/'catalogue.json').read_text())
 header=bytes.fromhex(manifest['run_id'])+b''.join(bytes.fromhex(manifest[k]) for k in ['bundle_sha256','catalogue_sha256','plan_sha256','target_sha256'])
 header+=b''.join(bytes.fromhex(c['fixture_sha256']+c['expectation_sha256']) for c in catalogue['cases'])+bytes([3,1])
 records=(folder/'results.bin').read_bytes();control=out/'records.input';control.write_bytes(header+records)
 subprocess.run([str(native),'records',str(control)],check=True)
 # Structural mutations with recomputed CRC are tested on real envelope boundaries.
 import struct,zlib
 changed=bytearray(records);changed[5]=6;struct.pack_into('<I',changed,40+struct.unpack_from('<I',changed,32)[0],zlib.crc32(changed[:40+struct.unpack_from('<I',changed,32)[0]]))
 bad=out/'bad-record.input';bad.write_bytes(header+changed)
 assert subprocess.run([str(native),'records',str(bad)],stdout=subprocess.DEVNULL).returncode==2
 trials=[]
 def snapshot(run_dir):
  return {str(p.relative_to(run_dir)):sha(p) for p in run_dir.rglob('*') if p.is_file()}
 # Stop after begin+first function. Another process boot must reject before allocation.
 interrupted=build(out/'interrupted-bundle',selected)
 prior=run(interrupted,out/'interrupted',stop_after=2);assert prior['command_statuses']==[0,0]
 before=snapshot(out/'interrupted/runs')
 for label in ['blocked','blocked-again']:
  result=run(interrupted,out/label);assert result['command_statuses']==[41] and result['recovery_gate']['code']!=0
  assert snapshot(out/label/'runs')==before
  for name in ['install.bin','recovery-a.bin','recovery-b.bin']:
   assert (out/label/name).read_bytes()==(out/'interrupted'/name).read_bytes()
  trials.append(label);print('PASSED:',label,flush=True)
 # A confirmed failure before interruption stays visible on restart.
 failed=build(out/'failed-bundle',selected,fault=1)
 run(failed,out/'failed-interrupted',stop_after=2)
 result=run(failed,out/'failed-blocked');assert result['command_statuses']==[41] and result['recovery_gate']['failed_case_mask']==1
 trials.append('confirmed failure retained')
 entry=build(out/'entry-bundle',selected)
 stopped=run(entry,out/'entry-stopped',stop_symbol='_startup_probe')
 assert stopped['command_statuses']==[0] and not stopped['returned_to_mos_prompt']
 blocked=run(entry,out/'entry-blocked')
 assert blocked['command_statuses']==[41] and blocked['recovery_gate']['phase']==4 and blocked['recovery_gate']['case_key']==1
 assert snapshot(out/'entry-stopped/runs')==snapshot(out/'entry-blocked/runs')
 trials.append('actual case-entry stop');print('PASSED: case-entry checkpoint identifies interrupted case',flush=True)
 mtools=ROOT/'.emulator/tools/mtools/usr/bin'
 def mutation(name,mutate):
  dest=out/(name+'-bundle');shutil.copytree(bundle,dest);mutate(dest)
  result=run(dest,out/name);assert result['command_statuses']==[41] and result['recovery_gate']['code']!=0,(name,result)
  assert len(result['reports'])==2,(name,result)
  assert all(r['report']['verdict']!='ALL TESTS PASSED' for r in result['reports']),(name,result)
  trials.append(name);print('PASSED:',name,flush=True)
 def put(dest,path,data):
  source=out/'mutation.bin';source.write_bytes(data)
  subprocess.run([str(mtools/'mcopy'),'-o','-i',str(dest/'sd.img')+'@@1048576',str(source),'::/'+path],check=True)
 def delete(dest,path):
  subprocess.run([str(mtools/'mdel'),'-i',str(dest/'sd.img')+'@@1048576','::/'+path],check=True)
 inspect_bundle=out/'inspect-bundle';shutil.copytree(bundle,inspect_bundle)
 put(inspect_bundle,'autoexec.txt',b'LOAD /mos-tests/runner.bin\nRUN . inspect\n')
 inspected=run(inspect_bundle,out/'inspect')
 assert inspected['command_statuses']==[0] and inspected['recovery_gate']['code']==0 and len(inspected['reports'])==2
 for name in ['install.bin','recovery-a.bin','recovery-b.bin']:
  assert (out/'inspect'/name).read_bytes()==(out/'repeat'/name).read_bytes()
 assert snapshot(out/'inspect/runs')==snapshot(out/'repeat/runs')
 trials.append('read-only inspection')
 mutation('missing-slot',lambda d:delete(d,'mos-tests/recovery-b.bin'))
 damaged=bytearray((out/'repeat/recovery-b.bin').read_bytes());damaged[248]^=1
 mutation('corrupt-slot',lambda d:put(d,'mos-tests/recovery-b.bin',damaged))
 mutation('damaged-results',lambda d:put(d,'mos-tests/runs/'+first_dir.name+'/results.bin',records[:-1]))
 mutation('damaged-manifest',lambda d:put(d,'mos-tests/runs/'+first_dir.name+'/plan.json',b'{}\n'))
 mutation('oversize-manifest',lambda d:put(d,'mos-tests/runs/'+first_dir.name+'/plan.json',b' '*16385))
 # Completed test failures do not masquerade as an interrupted installation.
 complete_failure=build(out/'complete-failure-bundle',selected,fault=1)
 for name in ['complete-failure','complete-failure-repeat']:
  result=run(complete_failure,out/name)
  assert result['command_statuses']==[0]*4 and result['recovery_gate']['code']==0
  assert all(r['report']['verdict']=='FAILURES' and r['report']['failed_tests']==1 for r in result['reports'])
 trials.append('completed failure permits normal repeat')
 # Observer evidence can only weaken completion, never remove confirmed outcomes.
 destination=out/'observer-incomplete'
 result=subprocess.run([sys.executable,str(ROOT/'scripts/report_results.py'),'--run',str(folder),'--output',str(destination),'--incomplete-reason','Qualification: final journal publication was not confirmed.'],capture_output=True,text=True)
 report=json.loads((destination/'report.json').read_text())
 assert result.returncode==2 and report['verdict']=='INCOMPLETE' and report['counts']['PASSED']==2 and result.stdout.startswith('INCOMPLETE')
 trials.append('observer uncertainty overrides complete stream')
 (out/'result.json').write_text(json.dumps({'passed':True,'native_bit_corruptions':2048,'transition_decisions':121,'raw_trials':trials,'clean_and_repeat':True,'hardware_tested':False},indent=2)+'\n')
 print('PASSED: W02 recovery gate controls; dispositions remain W03.',flush=True)
if __name__=='__main__':main()
