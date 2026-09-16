"""Run an existing raw startup image headlessly, collect card results and decode them."""
from pathlib import Path
import argparse,json,os,pty,re,select,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from run_smoke import ANSI,symbol,sha
from check_capture import memory
PY=ROOT.parents[1]/'.venv/bin/python'
def run(bundle,out,stop_after=None):
    out.mkdir(parents=True,exist_ok=False);image=bundle/'sd.img';maps=(bundle/'runner.map').read_text();done=symbol(maps,'_startup_command_done');status=symbol(maps,'_startup_status')
    mosmap=(ROOT/'.emulator/firmware/mos_platform.map').read_text();prompt=int(re.search(r'^_mos_input\s+C:([0-9A-Fa-f]+)',mosmap,re.M)[1],16)
    target=json.loads((bundle/'sdcard/mos-tests/target.json').read_text())
    assert target['backend']=='emulator','headless observer requires an emulator bundle'
    actual={key:sha(ROOT/'.emulator'/name) for key,name in [('mos_binary_sha256','firmware/mos_platform.bin'),('mos_map_sha256','firmware/mos_platform.map'),('emulator_binary_sha256','fab-agon-emulator.bin'),('vdp_binary_sha256','firmware/vdp_platform.so')]}
    assert all(target[k]==v for k,v in actual.items()),'profile changed since bundle preparation'
    raw=bytearray();master,slave=pty.openpty();proc=None;statuses=[];start=time.monotonic();stopped=False
    try:
        proc=subprocess.Popen([str(PY),str(ROOT/'scripts/run_emulator.py'),'--image',str(image),'-u','-d','-b','0'],stdin=slave,stdout=slave,stderr=slave,start_new_session=True);os.close(slave)
        def wait(off):
            deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                if b'>> ' in ANSI.sub(b'',bytes(raw[off:])):return
                if select.select([master],[],[],.1)[0]:raw.extend(os.read(master,65536))
                if proc.poll() is not None:raise RuntimeError('emulator exited before debugger stop')
            raise TimeoutError('startup failed to reach bounded debugger stop')
        def command(s):
            off=len(raw);os.write(master,(s+'\n').encode());wait(off);return ANSI.sub(b'',bytes(raw[off:])).decode(errors='replace').replace('\r','')
        wait(0);command(f'break ${done:x}');command(f'break ${prompt:x}');command('delete $0')
        for i in range(10):
            result=command('c')
            if re.search(r'\* '+f'{prompt:06x}'+':',result):stopped=True;break
            assert re.search(r'\* '+f'{done:06x}'+':',result),result
            statuses.append(memory(command(f'mem ${status:x} 1'),status,1)[0])
            if stop_after and len(statuses)==stop_after:break
        else:raise RuntimeError('too many invocations')
        ram=memory(command('mem $b7e000 8192'),0xb7e000,8192);(out/'sram.bin').write_bytes(ram)
        os.write(master,b'exit\n');proc.wait(timeout=5);assert proc.returncode==0
        mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy';subprocess.run([str(mcopy),'-s','-i',str(image)+'@@1048576','::/mos-tests/runs',str(out)],check=True)
        reports=[]
        for folder in sorted((out/'runs').iterdir()):
            if not folder.is_dir():continue
            dest=out/('report-'+folder.name)
            cmd=[str(PY),str(ROOT/'scripts/report_results.py'),'--run',str(folder),'--output',str(dest),'--colour','never']
            # Current SRAM belongs only to the newest run; older runs remain file-only.
            if folder.name in [ram[8:24].hex(),ram[136:152].hex()]:cmd+=['--sram',str(out/'sram.bin'),'--recovery-note','Fab debugger SRAM acquired at completed boot or deliberate stop, before reset; Linux raw SD image']
            result=subprocess.run(cmd,capture_output=True,text=True);(out/('report-'+folder.name+'.stdout.txt')).write_text(result.stdout+result.stderr);reports.append({'run':folder.name,'exit':result.returncode,'report':json.loads((dest/'report.json').read_text())})
        current=ram[8:24].hex() if ram[:4]==b'MSTC' else None
        receipt={'runtime_verified':actual,'current_run':current,'command_statuses':statuses,'returned_to_mos_prompt':stopped,'reports':reports,'elapsed_seconds':time.monotonic()-start,'cpu_throttling':'disabled (-u); no timing claims'}
        (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        os.close(master);(out/'debugger.raw.txt').write_bytes(raw);(out/'debugger.txt').write_bytes(ANSI.sub(b'',bytes(raw)))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--bundle',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();result=run(a.bundle.resolve(),a.output.resolve())
    current=next((r for r in result['reports'] if r['run']==result['current_run']),None)
    if current:
        from report_results import render
        print(render(current['report']),end='')
    else:print('INCOMPLETE: no validated current run; command statuses '+str(result['command_statuses'])+'. Evidence saved in '+str(a.output.resolve()))
    if any(result['command_statuses']) or not result['returned_to_mos_prompt'] or current is None:return 2
    return current['exit']
if __name__=='__main__':sys.exit(main())
