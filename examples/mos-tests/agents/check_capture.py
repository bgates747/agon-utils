"""Independent Fab state-vs-SRAM qualification of synthetic capture controls."""
from pathlib import Path
import argparse,json,os,pty,re,select,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_smoke import ANSI,symbol,sha
PY=ROOT.parents[1]/'.venv/bin/python'

def memory(text,start,length):
    data={}
    for address,raw in re.findall(r'^([0-9a-f]{6}): ((?:[0-9a-f]{2} )+)\|',text,re.M):
        a=int(address,16)
        for i,v in enumerate(bytes.fromhex(raw)):data[a+i]=v
    return bytes(data[start+i] for i in range(length))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    app=ROOT/'apps/capture-controls'
    with (out/'build.txt').open('w') as f:subprocess.run(['make','V='],cwd=app,stdout=f,stderr=subprocess.STDOUT,check=True)
    binary=app/'bin/capture-controls.bin';mapfile=binary.with_suffix('.map');maps=mapfile.read_text()
    symbols={n:symbol(maps,n) for n in ['_capture_before','_capture_after','_sample_done','_controls_done','_sample_index','_ram_upper']}
    (out/'identity.json').write_text(json.dumps({'binary':sha(binary),'map':sha(mapfile),'symbols':symbols,'backend':'Linux headless raw SD image','runtime':{n:sha(ROOT/'.emulator'/n) for n in ['fab-agon-emulator.bin','firmware/mos_platform.bin','firmware/mos_platform.map','firmware/vdp_platform.so']}},indent=2)+'\n')
    with (out/'disassembly.txt').open('w') as f:subprocess.run(['/home/smith/Agon/agondev/release/bin/ez80-none-elf-objdump','-dr',str(app/'obj/probe.o')],stdout=f,check=True)
    image=out/'sd.img';subprocess.run([str(PY),str(ROOT/'scripts/prepare_sd_image.py'),'--binary',str(binary),'--output',str(image)],stdout=subprocess.DEVNULL,check=True)
    raw=bytearray(); master,slave=pty.openpty();proc=None;results=[]
    try:
        proc=subprocess.Popen([str(PY),str(ROOT/'scripts/run_emulator.py'),'--image',str(image),'-d','-b','0'],stdin=slave,stdout=slave,stderr=slave,start_new_session=True);os.close(slave)
        def wait(offset):
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                if b'>> ' in ANSI.sub(b'',bytes(raw[offset:])):return
                if select.select([master],[],[],.1)[0]:raw.extend(os.read(master,65536))
                if proc.poll() is not None:raise RuntimeError('emulator exited')
            raise TimeoutError('no debugger prompt')
        def command(s):
            off=len(raw);os.write(master,(s+'\n').encode());wait(off)
            return ANSI.sub(b'',bytes(raw[off:])).decode(errors='replace').replace('\r','')
        wait(0)
        for n in ['_capture_before','_capture_after']:command(f'trigger ${symbols[n]:x} state')
        command(f'break ${symbols["_sample_done"]:x}');command(f'break ${symbols["_controls_done"]:x}');command('delete $0')
        for expected in json.loads((ROOT/'tests/capture/expected.json').read_text()):
            transcript=command('c');states=re.findall(r'\* ([0-9a-f]{6}):([^\n]*)',transcript)
            saved=memory(command('mem $b7e900 64'),0xb7e900,64)
            index=memory(command(f'mem ${symbols["_sample_index"]:x} 3'),symbols['_sample_index'],3)
            assert int.from_bytes(index,'little')==expected['index']
            entry,exit=saved[:32],saved[32:]
            for half,name in [(entry,'_capture_before'),(exit,'_capture_after')]:
                st=[s for addr,s in states if int(addr,16)==symbols[name]];assert len(st)==1,(expected,states)
                registers={n:int(v,16) for n,v in re.findall(r'([A-Z]+):([0-9a-f]+)',st[0])}
                for field,offset,width in [('AF',0,2),('BC',2,3),('DE',5,3),('HL',8,3),('IX',11,3),('IY',14,3),('SPL',17,3)]:
                    value=registers[field]+(3 if field=='SPL' else 0)
                    assert int.from_bytes(half[offset:offset+width],'little')==value,(expected,name,field,half.hex(),st)
                assert int.from_bytes(half[20:23],'little')==symbols[name]
                assert half[23:]==bytes.fromhex('000100ff0300000000'),half.hex()
            # Independent delta oracle from expected.json; PC differs by design.
            if expected['sp_delta']:
                assert int.from_bytes(exit[17:20],'little')==int.from_bytes(entry[17:20],'little')+3
                assert entry[:17]==exit[:17]
            else:
                want=bytearray(entry[:20])
                if expected['offset'] is not None:want[expected['offset']]^=expected['xor']
                assert exit[:20]==want,(expected,entry.hex(),exit.hex(),want.hex())
            results.append({'control':expected,'entry':entry.hex(),'exit':exit.hex(),'passed':True})
        command('c')
        ram=memory(command('mem $b7e000 8192'),0xb7e000,8192)
        assert ram[:0x900]==b'\xc7'*0x900 and ram[0x940:]==b'\xc7'*(8192-0x940),'SRAM guard changed'
        mapping=memory(command(f'mem ${symbols["_ram_upper"]:x} 2'),symbols['_ram_upper'],2)
        assert mapping==bytes.fromhex('b780'),mapping.hex()
        (out/'sram.bin').write_bytes(ram)
        os.write(master,b'exit\n');proc.wait(timeout=5);assert proc.returncode==0
        (out/'result.json').write_text(json.dumps({'passed':True,'controls':results,'mapping':mapping.hex(),'guards_intact':True,'capture_survived_reporting_clobbers':True,'limitations':['IFF unavailable','alternate registers not captured','SP deviation injected after return','hardware untested']},indent=2)+'\n')
        print(f'PASSED: {len(results)} synthetic controls matched independent debugger state and expected deltas; SRAM guards intact.')
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        os.close(master);(out/'debugger.raw.txt').write_bytes(raw)
        (out/'debugger.txt').write_bytes(ANSI.sub(b'',bytes(raw)))
        if not (out/'result.json').exists():(out/'incomplete.json').write_text(json.dumps({'completed_controls':len(results),'passed':False})+'\n')
if __name__=='__main__':main()
