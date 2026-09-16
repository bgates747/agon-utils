"""Build a copyable startup bundle and optionally deploy it into a fresh raw image."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,struct,subprocess,uuid,zlib
from plan_run import prepare,CAT
ROOT=Path(__file__).resolve().parents[1];PY=ROOT.parents[1]/'.venv/bin/python'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def script_text(functions):
    lines=['# MOS tests: comment out or delete BOTH lines of a function group.','LOAD /mos-tests/runner.bin','RUN . begin']
    for f in functions:lines+=['','# '+f,'LOAD /mos-tests/runner.bin','RUN . function '+f]
    lines+=['','LOAD /mos-tests/runner.bin','RUN . finalize',''];return '\n'.join(lines)
def build(out,script=None,backend='emulator',target=None,fault=0,image=True):
    out.mkdir(parents=True,exist_ok=False);sd=out/'sdcard';folder=sd/'mos-tests';folder.mkdir(parents=True);(folder/'runs').mkdir()
    cat,_=prepare();cases=cat['cases'];assert [c['key'] for c in cases]==[1,2,3]
    assert [c['function'] for c in cases]==['synthetic_preserve','synthetic_clobber','synthetic_capability']
    assert all(c['samples']==[0,1] for c in cases)
    assert [c['capabilities'] for c in cases]==[[],['capture.primary'],['uart.peer']]
    assert json.loads((ROOT/'fixtures/synthetic/preserve.json').read_text())['delta']=='none'
    assert json.loads((ROOT/'fixtures/synthetic/ix-upper.json').read_text())['delta']=='IX upper byte xor80 only'
    app=ROOT/'apps/startup-runner'
    def array(data):return '{'+','.join(str(x) for x in data)+'}'
    header='#pragma once\n#include "../../runner/include/catalogue_generated.h"\n'
    header+='static const uint8_t BACKEND=%d;\n'%(1 if backend=='emulator' else 2)
    header+='static const char* const FUNCTIONS[3]={'+','.join(json.dumps(c['function']) for c in cases)+'};\n'
    header+='static const uint8_t CATALOGUE_DIGEST[32]='+array(bytes.fromhex(sha(CAT)))+';\n'
    header+='static const uint8_t CASE_HASHES[3][64]={'+','.join(array(bytes.fromhex(c['fixture_sha256']+c['expectation_sha256'])) for c in cases)+'};\n'
    (app/'include/generated.h').write_text(header)
    with (out/'build.txt').open('w') as log:subprocess.run(['make'],cwd=app,stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copy2(app/'bin/startup-runner.bin',folder/'runner.bin');shutil.copy2(app/'bin/startup-runner.map',out/'runner.map')
    shutil.copy2(CAT,folder/'catalogue.json')
    for f in (ROOT/'fixtures/synthetic').glob('*.json'):shutil.copy2(f,folder/f.name)
    shutil.copy2(ROOT/'fixtures/format-v1/capture-controls.json',folder/'capture-controls.json')
    toolchain=Path('/home/smith/Agon/agondev/release')
    write(folder/'toolchain.json',{'tools':{n:sha(toolchain/'bin'/n) for n in ['ez80-none-elf-clang','ez80-none-elf-as','ez80-none-elf-ld']},'source_files':{str(f.relative_to(ROOT)):sha(f) for base in [app/'src',app/'include',ROOT/'apps/runner/include',ROOT/'apps/runner/src'] for f in sorted(base.iterdir()) if f.is_file()}})
    if backend=='emulator':
        profile=ROOT/'.emulator';target={'schema':1,'backend':'emulator','declared_by':'Linux profile hashes at startup bundle preparation; hardware untested','mos_binary_sha256':sha(profile/'firmware/mos_platform.bin'),'mos_map_sha256':sha(profile/'firmware/mos_platform.map'),'toolchain_manifest_sha256':sha(folder/'toolchain.json'),'emulator_binary_sha256':sha(profile/'fab-agon-emulator.bin'),'vdp_binary_sha256':sha(profile/'firmware/vdp_platform.so')}
    else:
        if target is None:raise ValueError('hardware bundle requires explicit target.json')
        target=json.loads(target.read_text());assert target['backend']=='hardware';target['toolchain_manifest_sha256']=sha(folder/'toolchain.json')
    write(folder/'target.json',target)
    for mask in range(1,8):
        selected=[c for i,c in enumerate(cases) if mask&(1<<i)]
        write(folder/f'plan-{mask}.json',{'schema':1,'catalogue_sha256':sha(CAT),'selectors':['function:'+c['function'] for c in selected],'case_keys':[c['key'] for c in selected],'backend':backend,'capabilities':['capture.primary'],'script_sha256':'@'*64})
    (folder/'fault.bin').write_bytes(bytes([fault]))
    files=sorted(f for f in folder.iterdir() if f.is_file())
    (folder/'files.lst').write_text(''.join(f'{f.name} {sha(f)}\n' for f in files))
    write(folder/'bundle.json',{'schema':1,'catalogue_sha256':sha(CAT),'artifacts':[{'path':f.name,'size':f.stat().st_size,'sha256':sha(f)} for f in files+[folder/'files.lst']]})
    namespace=uuid.uuid4().bytes[:8];counter=namespace+bytes(8);(folder/'install.bin').write_bytes(counter+struct.pack('<I',zlib.crc32(counter))+b'MSTI')
    (sd/'autoexec.txt').write_bytes(script.read_bytes() if script else script_text([c['function'] for c in cases]).encode())
    (sd/'!boot.obey').write_bytes(b'SET KEYBOARD 1\nEXEC /autoexec.txt\n')
    write(out/'bundle-receipt.json',{'bundle_sha256':sha(folder/'bundle.json'),'namespace':namespace.hex(),'backend':backend,'fault_injection':fault,'initial_script_sha256':sha(sd/'autoexec.txt'),'binary_sha256':sha(folder/'runner.bin'),'map_sha256':sha(out/'runner.map')})
    if image:
        disk=out/'sd.img';subprocess.run([str(PY),str(ROOT/'scripts/prepare_sd_image.py'),'--binary',str(folder/'runner.bin'),'--output',str(disk)],stdout=subprocess.DEVNULL,check=True)
        mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy';spec=str(disk)+'@@1048576'
        for name in ['mos-tests','autoexec.txt','!boot.obey']:subprocess.run([str(mcopy),'-o','-s','-i',spec,str(sd/name),'::/'],check=True)
        # Independently verify every deployed source file through the final partition.
        checks=out/'readback';checks.mkdir()
        for f in sd.rglob('*'):
            if not f.is_file():continue
            dest=checks/str(f.relative_to(sd)).replace('/','_');subprocess.run([str(mcopy),'-i',spec,'::/'+f.relative_to(sd).as_posix(),str(dest)],check=True);assert dest.read_bytes()==f.read_bytes()
        write(out/'deployed-image.json',{'sha256':sha(disk),'files_verified':len(list(checks.iterdir()))})
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--script',type=Path);ap.add_argument('--backend',choices=['emulator','hardware'],default='emulator');ap.add_argument('--target',type=Path);ap.add_argument('--no-image',action='store_true');ap.add_argument('--qualification-fault',type=int,choices=[0,1,2,3],default=0);a=ap.parse_args()
    build(a.output.resolve(),a.script,a.backend,a.target,a.qualification_fault,not a.no_image);print('PREPARED: copyable sdcard/ bundle; no tests executed. '+str(a.output.resolve()))
if __name__=='__main__':main()
