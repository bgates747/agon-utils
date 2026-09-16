"""Qualify the real boot chain, edited selections, continuation and stopping."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from startup_bundle import build,script_text
from run_startup import run
FUNCTIONS=['synthetic_preserve','synthetic_clobber','synthetic_capability']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    binary=out/'primitive';subprocess.run(['g++','-std=c++14','-I'+str(ROOT/'apps/startup-runner/include'),str(ROOT/'tests/startup/primitive.cpp'),'-o',str(binary)],check=True)
    for n in [0,1,3,55,56,63,64,65,127,128,255,1024,8192]:
        data=bytes((i*37+11)&255 for i in range(n));assert subprocess.check_output([str(binary)],input=data).decode().strip()==hashlib.sha256(data).hexdigest()
    continuation=out/'continuation'
    subprocess.run(['g++','-std=c++14','-I'+str(ROOT/'apps/startup-runner/include'),'-I'+str(ROOT/'apps/runner/include'),str(ROOT/'tests/startup/continuation.cpp'),'-o',str(continuation)],check=True)
    subprocess.run([str(continuation)],check=True)
    scripts={}
    for mask in range(1,8):
        s=script_text([f for i,f in enumerate(FUNCTIONS) if mask&(1<<i)]);assert subprocess.check_output([str(binary),'parse'],input=s.encode()).decode().strip()==str(mask);scripts[mask]=s
    invalid=[scripts[7].replace('RUN . finalize',''),scripts[7].replace('RUN . begin',''),scripts[7].replace('synthetic_preserve','unknown'),scripts[7].replace('RUN . function synthetic_clobber','RUN . function synthetic_preserve'),scripts[7]+'DIR\n',scripts[7].replace('LOAD /mos-tests/runner.bin\n','',1),scripts[7].replace('RUN . begin','RUN . begin\x00')]
    for s in invalid:assert subprocess.run([str(binary),'parse'],input=s.encode(),capture_output=True).returncode==2
    checked=[]
    def trial(name,script,expected_status,expected_verdict=None,fault=0,stop=None):
        f=out/(name+'.txt');f.write_text(script);bundle=build(out/(name+'-bundle'),f,fault=fault);result=run(bundle,out/(name+'-run'),stop_after=stop)
        assert result['command_statuses']==expected_status,(name,result)
        assert result['returned_to_mos_prompt']==(stop is None),(name,result)
        if expected_verdict is not None:assert len(result['reports'])==1 and result['reports'][0]['report']['verdict']==expected_verdict,(name,result)
        else:assert not result['reports'],(name,result)
        checked.append({'name':name,'statuses':expected_status,'verdict':expected_verdict,'seconds':result['elapsed_seconds']});print('PASSED:',name,flush=True);return bundle,result
    full,full_result=trial('full',scripts[7],[0]*5,'NO FAILURES OBSERVED — coverage limited')
    assert full_result['reports'][0]['report']['counts']['PASSED']==2 and full_result['reports'][0]['report']['counts']['UNSUPPORTED']==1
    single,_=trial('single',scripts[1],[0]*3,'ALL TESTS PASSED')
    commented=scripts[7].replace('LOAD /mos-tests/runner.bin\nRUN . function synthetic_capability','# LOAD /mos-tests/runner.bin\n# RUN . function synthetic_capability')
    _,r=trial('commented-group',commented,[0]*4,'ALL TESTS PASSED');assert r['reports'][0]['report']['selected']==2
    _,r=trial('deliberate-failure',scripts[3],[0]*4,'FAILURES',fault=1);assert r['reports'][0]['report']['failed_tests']==1 and r['reports'][0]['report']['counts']['PASSED']==1
    trial('infrastructure-stop',scripts[3],[0,35],'INCOMPLETE',fault=2)
    trial('changed-script',scripts[3],[0,26],'INCOMPLETE',fault=3)
    trial('unknown-function',scripts[7].replace('synthetic_preserve','unknown'),[20])
    trial('missing-finalize',scripts[3],[0]*3,'INCOMPLETE',stop=3)
    _,missing=trial('missing-group',scripts[3],[0]*2,'INCOMPLETE',stop=2)
    assert missing['reports'][0]['report']['counts']['PASSED']==1
    # Second boot consumes the persisted counter and never overwrites the first run.
    first=next((out/'single-run/runs').iterdir());before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in first.iterdir() if f.is_file()}
    again=run(single,out/'repeat-run');assert again['command_statuses']==[0]*3 and len(again['reports'])==2
    original=out/'repeat-run/runs'/first.name;assert before=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in original.iterdir() if f.is_file()}
    ids=[bytes.fromhex(r['run']) for r in again['reports']];assert ids[0][:8]==ids[1][:8] and sorted(int.from_bytes(i[8:],'little') for i in ids)==[1,2];assert all(r['report']['verdict']=='ALL TESTS PASSED' for r in again['reports']);checked.append({'name':'repeat boot: monotonic identity and prior-run preservation'})
    # Missing begin/finalize are rejected by the same on-device parser before effects;
    # an interrupted valid script above proves actual missing finalization is incomplete.
    (out/'result.json').write_text(json.dumps({'passed':True,'native_sha_vectors':13,'continuation_controls':9,'valid_selections':7,'rejected_scripts':7,'trials':checked,'hardware_tested':False},indent=2)+'\n')
    print('PASSED: startup qualification complete; hardware untested.',flush=True)
if __name__=='__main__':main()
