"""Run an existing raw startup image headlessly, collect card results and decode them."""
from pathlib import Path
import argparse,json,os,pty,re,select,subprocess,sys,time,zlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'agents')]
from run_smoke import ANSI,symbol,sha
from check_capture import memory
PY=ROOT.parents[1]/'.venv/bin/python'
def run(bundle,out,stop_after=None,stop_symbol=None):
    out.mkdir(parents=True,exist_ok=False);image=bundle/'sd.img';maps=(bundle/'runner.map').read_text();done=symbol(maps,'_startup_command_done');status=symbol(maps,'_startup_status')
    mosmap=(ROOT/'.emulator/firmware/mos_platform.map').read_text();prompt=int(re.search(r'^_mos_input\s+C:([0-9A-Fa-f]+)',mosmap,re.M)[1],16)
    target=json.loads((bundle/'sdcard/mos-tests/target.json').read_text())
    assert target['backend']=='emulator','headless observer requires an emulator bundle'
    actual={key:sha(ROOT/'.emulator'/name) for key,name in [('mos_binary_sha256','firmware/mos_platform.bin'),('mos_map_sha256','firmware/mos_platform.map'),('emulator_binary_sha256','fab-agon-emulator.bin'),('vdp_binary_sha256','firmware/vdp_platform.so')]}
    assert all(target[k]==v for k,v in actual.items()),'profile changed since bundle preparation'
    stop_address=symbol(maps,stop_symbol) if stop_symbol else None
    diagnostic_address=symbol(maps,'_recovery_diagnostic') if '_recovery_diagnostic' in maps else None
    diagnostic=None
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
        wait(0)
        if stop_address is not None:command(f'break ${stop_address:x}')
        command(f'break ${done:x}');command(f'break ${prompt:x}');command('delete $0')
        for i in range(10):
            result=command('c')
            if re.search(r'\* '+f'{prompt:06x}'+':',result):stopped=True;break
            if stop_address is not None and re.search(r'\* '+f'{stop_address:06x}'+':',result):break
            assert re.search(r'\* '+f'{done:06x}'+':',result),result
            statuses.append(memory(command(f'mem ${status:x} 1'),status,1)[0])
            if stop_after and len(statuses)==stop_after:break
        else:raise RuntimeError('too many invocations')
        if diagnostic_address is not None:
            d=memory(command(f'mem ${diagnostic_address:x} 64'),diagnostic_address,64)
            diagnostic={'code':d[0],'phase':d[1],'case_key':int.from_bytes(d[4:8],'little'),'failed_case_mask':d[8],'run_id':d[16:32].hex()}
        ram=memory(command('mem $b7e000 8192'),0xb7e000,8192);(out/'sram.bin').write_bytes(ram)
        os.write(master,b'exit\n');proc.wait(timeout=5);assert proc.returncode==0
        mcopy=ROOT/'.emulator/tools/mtools/usr/bin/mcopy';subprocess.run([str(mcopy),'-s','-i',str(image)+'@@1048576','::/mos-tests/runs',str(out)],check=True)
        for name in ['recovery-a.bin','recovery-b.bin','install.bin']:
            result=subprocess.run([str(mcopy),'-i',str(image)+'@@1048576','::/mos-tests/'+name,str(out/name)],capture_output=True,text=True)
            if result.returncode:(out/(name+'.retrieval-error.txt')).write_text(result.stderr)
        # Expose the expected generation for explicit human requests. Target recover
        # still validates the complete pair/transition and exact subject itself.
        if diagnostic is not None:
            valid_slots=[]
            for name in ['recovery-a.bin','recovery-b.bin']:
                p=out/name
                b=p.read_bytes() if p.exists() else b''
                if len(b)==256 and b[:8]==b'MSTJ\x01\x00\x00\x01' and b[252]==0xa5 and int.from_bytes(b[248:252],'little')==zlib.crc32(b[:248]):
                    valid_slots.append(b)
            diagnostic['journal_generation']=str(max(int.from_bytes(b[16:24],'little') for b in valid_slots)) if len(valid_slots)==2 else None
        recovery_copy=subprocess.run([str(mcopy),'-s','-i',str(image)+'@@1048576','::/mos-tests/recovery',str(out)],capture_output=True,text=True)
        if recovery_copy.returncode:(out/'recovery.retrieval-note.txt').write_text(recovery_copy.stderr)
        reports=[]
        for folder in sorted((out/'runs').iterdir()):
            if not folder.is_dir():continue
            dest=out/('report-'+folder.name)
            cmd=[str(PY),str(ROOT/'scripts/report_results.py'),'--run',str(folder),'--output',str(dest),'--colour','never']
            # Current SRAM belongs only to the newest run; older runs remain file-only.
            if folder.name in [ram[8:24].hex(),ram[136:152].hex()]:cmd+=['--sram',str(out/'sram.bin'),'--recovery-note','Fab debugger SRAM acquired at completed boot or deliberate stop, before reset; Linux raw SD image']
            subject=diagnostic['run_id'] if diagnostic else None
            if (any(statuses) or diagnostic and diagnostic['code']) and (not subject or subject=='0'*32 or subject==folder.name):
                cmd+=['--incomplete-reason','Startup observer recorded an unresolved journal or command failure; see recovery_gate, command_statuses, journal bytes and debugger transcript in '+str(out)]
            result=subprocess.run(cmd,capture_output=True,text=True);(out/('report-'+folder.name+'.stdout.txt')).write_text(result.stdout+result.stderr);reports.append({'run':folder.name,'exit':result.returncode,'report':json.loads((dest/'report.json').read_text())})
        current=ram[8:24].hex() if ram[:4]==b'MSTC' else None
        receipt={'controlled_stop_symbol':stop_symbol,'recovery_gate':diagnostic,'runtime_verified':actual,'current_run':current,'command_statuses':statuses,'returned_to_mos_prompt':stopped,'reports':reports,'elapsed_seconds':time.monotonic()-start,'cpu_throttling':'disabled (-u); no timing claims'}
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
    gate=result.get('recovery_gate')
    if gate and gate['code']:
        reasons={1:'missing, corrupt or conflicting journal/allocation state',2:'previous execution is unresolved',3:'run history does not reconcile',4:'unreadable, unsupported or invalid saved evidence',5:'record completion is unresolved',6:'recovery storage unavailable',7:'disposition/legacy state needs unsupported recovery action',8:'inspection limit exceeded',9:'same-boot session disagrees with journal',10:'disposition evidence or publication could not be validated',11:'explicit request or selection was rejected'}
        print('INCOMPLETE: recovery gate blocked test execution — '+reasons.get(gate['code'],'journal publication error')+'.')
        phases=['idle','allocating','between cases','case intent','in case','case completed; cleanup pending','finalizing','complete','disposing','parked','armed']
        phase=phases[gate['phase']] if gate['phase']<len(phases) else 'unverified'
        catalogue=json.loads((a.bundle/'sdcard/mos-tests/catalogue.json').read_text())['cases']
        names={c['key']:c['id'] for c in catalogue}
        failed=[i+1 for i in range(3) if gate['failed_case_mask']&(1<<i)]
        print('Confirmed failed tests: '+str(len(failed))+(' ('+', '.join(names.get(k,str(k)) for k in failed)+')' if failed else '')+'.')
        print('Retained run: '+gate['run_id']+'; phase: '+phase+'; last active case: '+names.get(gate['case_key'],'none established')+'.')
        print('Expected journal generation: '+str(gate.get('journal_generation'))+'.')
        print('No retry was authorized. Original evidence is preserved; use the explicit recovery tools after inspection.')
    elif any(result['command_statuses']):
        print('INCOMPLETE: startup stopped with command statuses '+str(result['command_statuses'])+'. A completed file alone does not establish successful journal/close finalization.')
        if current:
            print('Confirmed failed tests: '+str(current['report']['failed_tests'])+'.')
    elif current:
        from report_results import render
        print(render(current['report']),end='')
    else:print('INCOMPLETE: no validated current run; command statuses '+str(result['command_statuses'])+'. Evidence saved in '+str(a.output.resolve()))
    if any(result['command_statuses']) or not result['returned_to_mos_prompt'] or current is None:return 2
    return current['exit']
if __name__=='__main__':sys.exit(main())
