"""Qualify recorder using native faults and real MOS raw-image checkpoints."""
from pathlib import Path
import argparse,json,os,pty,select,shutil,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/recording'),str(ROOT/'agents')]
from run_smoke import ANSI,symbol,sha
from check_capture import memory
from verify import records,slots
PY=ROOT.parents[1]/'.venv/bin/python'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    (out/"incomplete.json").write_text('{"passed": false}\n')
    with (out/'native.txt').open('w') as log:
        subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I',str(ROOT/'apps/runner/include'),str(ROOT/'tests/recording/check.cpp'),'-o',str(out/'native-check')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'native-check'),str(ROOT/'fixtures/format-v1'),str(out)],stdout=log,stderr=subprocess.STDOUT,check=True)
    # Reject every truncated prefix and mutations without consulting the encoder.
    truncated=mutated=0
    for path in (ROOT/'fixtures/format-v1').glob('*.bin'):
        if path.stem not in ['run-start','case-start','observation','case-end','checkpoint-error','run-end']:continue
        golden=path.read_bytes()
        for end in range(1,len(golden)):
            try:records(golden[:end])
            except ValueError:truncated+=1
            else:raise AssertionError(('accepted truncation',path.name,end))
        for index in range(len(golden)):
            bad=bytearray(golden);bad[index]^=1
            try:records(bad)
            except ValueError:mutated+=1
            else:raise AssertionError(('accepted mutation',path.name,index))
    (out/'wire-checks.json').write_text(json.dumps({'rejected_truncations':truncated,'rejected_single_bit_mutations':mutated})+'\n')
    for name in ['bad-crc.bin','missing-commit.bin']:
        try:records((ROOT/'fixtures/format-v1'/name).read_bytes())
        except ValueError:pass
        else:raise AssertionError(name)
    for f in out.glob('failure-*.sram'):
        ram=f.read_bytes();assert slots(ram)
        err=records(ram[0xd00:0xd3d]);assert len(err)==1 and err[0][0]==5
    app=ROOT/'apps/recording-controls'
    with (out/'build.txt').open('w') as f:subprocess.run(['make'],cwd=app,stdout=f,stderr=subprocess.STDOUT,check=True)
    binary=app/'bin/recording-controls.bin';maps=binary.with_suffix('.map');text=maps.read_text()
    shutil.copy2(binary,out/binary.name);shutil.copy2(maps,out/maps.name)
    symbols={n:symbol(text,n) for n in ['_recording_done','_recording_status']}
    (out/'identity.json').write_text(json.dumps({'backend':'Linux headless raw SD image','binary':sha(binary),'map':sha(maps),'symbols':symbols,'compiler_sha256':sha(Path('/home/smith/Agon/agondev/release/bin/ez80-none-elf-clang')),'sources':{str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'apps/runner/include').glob('*.h'))+sorted((ROOT/'apps/runner/src').glob('*.asm'))+sorted((app/'src').glob('*'))},'runtime':{n:sha(ROOT/'.emulator'/n) for n in ['fab-agon-emulator.bin','firmware/mos_platform.bin','firmware/mos_platform.map','firmware/vdp_platform.so']},'limits':['synthetic fixture hashes; not an authenticated general suite run','hardware untested']},indent=2)+'\n')
    with (out/'disassembly.txt').open('w') as f:subprocess.run(['/home/smith/Agon/agondev/release/bin/ez80-none-elf-objdump','-dr',str(app/'obj/main.o')],stdout=f,check=True)
    with (out/'probe-disassembly.txt').open('w') as f:subprocess.run(['/home/smith/Agon/agondev/release/bin/ez80-none-elf-objdump','-dr',str(app/'obj/probe.o')],stdout=f,check=True)
    image=out/'sd.img';subprocess.run([str(PY),str(ROOT/'scripts/prepare_sd_image.py'),'--binary',str(binary),'--output',str(image)],stdout=subprocess.DEVNULL,check=True)
    run_id=uuid.uuid4().bytes;(out/'run.id').write_bytes(run_id)
    mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy'
    subprocess.run([str(mcopy),'-i',str(image)+'@@1048576',str(out/'run.id'),'::/run.id'],check=True)
    (out/'deployed-image.json').write_text(json.dumps({'sha256':sha(image),'run_id':run_id.hex()})+'\n')
    raw=bytearray();master,slave=pty.openpty();proc=None
    try:
        proc=subprocess.Popen([str(PY),str(ROOT/'scripts/run_emulator.py'),'--image',str(image),'-d','-b','0'],stdin=slave,stdout=slave,stderr=slave,start_new_session=True);os.close(slave)
        def wait(offset):
            deadline=time.monotonic()+45
            while time.monotonic()<deadline:
                if b'>> ' in ANSI.sub(b'',bytes(raw[offset:])):return
                if select.select([master],[],[],.1)[0]:raw.extend(os.read(master,65536))
                if proc.poll() is not None:raise RuntimeError('emulator exited')
            raise TimeoutError('no debugger prompt')
        def command(s):
            off=len(raw);os.write(master,(s+'\n').encode());wait(off)
            return ANSI.sub(b'',bytes(raw[off:])).decode(errors='replace').replace('\r','')
        wait(0);command(f'break ${symbols["_recording_done"]:x}');command('delete $0');command('c')
        status=memory(command(f'mem ${symbols["_recording_status"]:x} 1'),symbols['_recording_status'],1)
        ram=memory(command('mem $b7e000 8192'),0xb7e000,8192);(out/'sram.bin').write_bytes(ram)
        assert status==b'\x01',('target status',status.hex())
        os.write(master,b'exit\n');proc.wait(timeout=5);assert proc.returncode==0
        subprocess.run([str(mcopy),'-i',str(image)+'@@1048576','::/results.bin',str(out/'results.bin')],check=True)
        rows=records((out/'results.bin').read_bytes())
        assert [(r[0],r[1],r[2]) for r in rows]==[(1,1,0),(2,2,1),(3,3,1),(4,4,1),(2,5,2),(3,6,2),(4,7,2),(6,8,0)]
        assert all(r[4]==run_id for r in rows)
        for r in rows:
            if r[0]==3:assert r[3][16:36]==r[3][48:68] and r[3][80:100]==b'\xff'*20
            if r[0]==4:assert r[3]==bytes.fromhex('0100010001000000000000000100000000000000')
        assert rows[-1][3][4:36]==b'\x02'+bytes(31)
        valid=slots(ram);latest=max(valid,key=lambda s:s['generation']);assert latest['state']==6 and latest['confirmed']==8 and latest['used']==0 and latest['run']==run_id.hex()
        assert ram[0xd00:0xe00]==bytes(256)
        assert ram[0x940:0xd00]==b'\xc7'*(0xd00-0x940) and ram[0xe00:]==b'\xc7'*(8192-0xe00)
        # Reboot the same image: CREATE_NEW must reject prior results, preserving bytes.
        original=(out/'results.bin').read_bytes()
        os.close(master);master,slave=pty.openpty()
        offset=len(raw)
        proc=subprocess.Popen([str(PY),str(ROOT/'scripts/run_emulator.py'),'--image',str(image),'-d','-b','0'],stdin=slave,stdout=slave,stderr=slave,start_new_session=True);os.close(slave)
        wait(offset);command(f'break ${symbols["_recording_done"]:x}');command('delete $0');command('c')
        status=memory(command(f'mem ${symbols["_recording_status"]:x} 1'),symbols['_recording_status'],1)
        collision=memory(command('mem $b7e000 8192'),0xb7e000,8192)
        (out/'collision.sram').write_bytes(collision)
        assert status==b'\x02'
        emergency=records(collision[0xd00:0xd3d])[0]
        assert emergency[0]==5 and emergency[3][2]==5
        assert int.from_bytes(emergency[3][4:8],'little')==8  # FatFS FR_EXIST
        assert max(slots(collision),key=lambda s:s['generation'])['state']==5
        os.write(master,b'exit\n');proc.wait(timeout=5);assert proc.returncode==0
        subprocess.run([str(mcopy),'-i',str(image)+'@@1048576','::/results.bin',str(out/'results-after-collision.bin')],check=True)
        assert (out/'results-after-collision.bin').read_bytes()==original
        (out/'result.json').write_text(json.dumps({'passed':True,'records':len(rows),'captured_cases':2,'prior_result_preserved_on_collision':True,'confirmed_sequence':8,'guards_intact':True,'native':(out/'native.txt').read_text(),'limitations':['hardware untested','no power-loss durability claim','full decoder qualification continues in W05','synthetic fixture identity only']},indent=2)+'\n')
        (out/'incomplete.json').unlink()
        print('PASSED: recorder fault controls and two captured target cases; eight records recovered from raw SD, guards intact.')
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        os.close(master);(out/'debugger.raw.txt').write_bytes(raw);(out/'debugger.txt').write_bytes(ANSI.sub(b'',bytes(raw)))
        if not (out/'result.json').exists():(out/'incomplete.json').write_text('{"passed": false}\n')
if __name__=='__main__':main()
