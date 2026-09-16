"""Independent literal fixtures exercise the production parser/report; no encoder reuse."""
from pathlib import Path
import argparse,hashlib,json,struct,sys,zlib,copy,subprocess
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import report_results as sut
U16=lambda n:struct.pack('<H',n)
U32=lambda n:struct.pack('<I',n)
ID=bytes(range(16))
def digest(b):return hashlib.sha256(b).hexdigest()
def write(root,name,obj):
    b=(json.dumps(obj,indent=2)+'\n').encode();(root/name).write_bytes(b);return digest(b)
def envelope(kind,seq,key,payload):
    b=b'MSTR'+bytes([1,kind])+U16(40)+ID+U32(seq)+U32(key)+U32(len(payload))+bytes(4)+payload
    return b+U32(zlib.crc32(b))+b'\xa5'
def fixture(root,oracle):
    root.mkdir();fixture=b'{"input": 10}\n';expect=b'{"expected": 10}\n';(root/'input.json').write_bytes(fixture);(root/'expected.json').write_bytes(expect);(root/'selection-script.txt').write_bytes(b'')
    keys=oracle['selected'];catalogue={'schema':1,'cases':[{'key':k,'id':f'case.{k}','function':f'function.{k}','route':'synthetic','group':'controls','expectation_sha256':digest(expect),'fixture_sha256':digest(fixture),'capabilities':[],'isolation':'pure','samples':[0],'timeout_ms':1000} for k in keys or [1]]}
    ch=write(root,'catalogue.json',catalogue);ph=write(root,'plan.json',dict(schema=1,catalogue_sha256=ch,selectors=['all'],case_keys=keys,backend='emulator',capabilities=[],script_sha256=digest(b'')))
    th=write(root,'target.json',dict(schema=1,backend='emulator',declared_by='independent synthetic fixture, not real hardware',**{k:'77'*32 for k in ['mos_binary_sha256','mos_map_sha256','toolchain_manifest_sha256','emulator_binary_sha256','vdp_binary_sha256']}))
    bh=write(root,'bundle.json',dict(schema=1,catalogue_sha256=ch,artifacts=[dict(path=name,size=len(b),sha256=digest(b)) for name,b in [('input.json',fixture),('expected.json',expect)]]))
    write(root,'run.json',dict(schema=1,run_id=ID.hex(),parent_run_id=None,bundle_sha256=bh,catalogue_sha256=ch,plan_sha256=ph,target_sha256=th))
    rows=[envelope(1,1,0,U16(1)+b'\x01\0'+U32(len(keys) or 1)+b''.join(bytes.fromhex(h) for h in [bh,ch,ph,th]))];counts=[0]*8
    for i,k in enumerate(keys):
        status=oracle['ends'][i]
        if status is None:break
        rows.append(envelope(2,len(rows)+1,k,U16(1)+U16(1)+bytes.fromhex(digest(fixture)+digest(expect))))
        d=sut.NAMES.index(status)+1;assertions=oracle.get('assertions',[1 if s in ['PASSED','FAILED'] else 0 for s in oracle['ends']])[i];failed=oracle.get('failed_assertions',[1 if s=='FAILED' else 0 for s in oracle['ends']])[i]
        obs=0
        if status in ['PASSED','FAILED','OBSERVED']:
            # A one-byte observed result; expected-error fixture captures its nonzero status.
            data=b'\x04' if oracle['id']=='expected-error-pass' else b'\x0a'
            rows.append(envelope(3,len(rows)+1,k,U16(1)+b'\x02\0'+U16(0)+U16(0)+U16(1)+U16(1)+U32(1)+data));obs=1
        reason=b'' if status=='PASSED' else b'operation returned an unexpected value' if status=='FAILED' else status.lower().encode()
        rows.append(envelope(4,len(rows)+1,k,U16(1)+bytes([d,0])+U32(assertions)+U32(failed)+U32(obs)+U16(len(reason))+bytes(2)+reason));counts[d-1]+=1
    if oracle['run_end']:rows.append(envelope(6,len(rows)+1,0,U16(1)+bytes(2)+b''.join(U32(n) for n in counts)+bytes.fromhex(ph)))
    (root/'results.bin').write_bytes(b''.join(rows));return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);checks=[]
    oracles=json.loads((ROOT/'fixtures/format-v1/report-oracles.json').read_text())
    for o in oracles:
        folder=out/o['id'];raw=fixture(folder,o)
        if not o['selected']:
            try:sut.manifests(folder)
            except ValueError:checks.append(o['id']);continue
            raise AssertionError('empty plan accepted')
        m=sut.manifests(folder);rows,issues=sut.scan(b''.join(raw),'fixture');r=sut.evaluate(m,rows,issues)
        assert r['verdict']==o['verdict'],(o['id'],r)
        assert r['counts']['PASSED']==o['passed'] and r['failed_tests']==o['failed_tests'],(o,r)
        plain=sut.render(r);colour=sut.render(r,True);assert '\x1b' not in plain
        if r['failed_ids']:
            assert plain.index('Failed tests:')<plain.index('Case details')
            assert '\x1b[97;41mFAILED\x1b[0m' in colour
        if r['verdict']=='ALL TESTS PASSED':assert colour.startswith('\x1b[97;42mPASSED\x1b[0m')
        (folder/'expected-report.txt').write_text(plain);checks.append(o['id'])
    base=out/'all-pass';m=sut.manifests(base);raw=(base/'results.bin').read_bytes();rows,issues=sut.scan(raw,'file');assert not issues
    def bad(name,data):
        rr,ii=sut.scan(data,name);result=sut.evaluate(m,rr,ii);assert result['verdict']!='ALL TESTS PASSED',(name,result);checks.append(name)
    for name,data in [('missing-run-start',b''.join(r['raw'] for r in rows[1:])),('missing-middle',b''.join(r['raw'] for r in rows if r['sequence']!=3)),('reordered',rows[1]['raw']+rows[0]['raw']+b''.join(r['raw'] for r in rows[2:])),('after-end',raw+envelope(2,9,1,rows[1]['payload'])),('unknown-key',raw.replace(b'impossible',b'impossible'))]:
        if name!='unknown-key':bad(name,data)
    altered=envelope(3,3,99,rows[2]['payload']);bad('unknown-key',b''.join(altered if r['sequence']==3 else r['raw'] for r in rows))
    foreign=bytearray(rows[2]['raw']);foreign[8]^=0xff;foreign[-5:-1]=U32(zlib.crc32(foreign[:-5]));bad('foreign-run',rows[0]['raw']+rows[1]['raw']+bytes(foreign)+b''.join(r['raw'] for r in rows[3:]))
    duplicate=sut.evaluate(m,rows+rows,[]);assert duplicate['verdict']=='ALL TESTS PASSED';checks.append('identical duplicates merge once')
    conflict=dict(rows[2]);conflict['raw']=envelope(3,3,1,rows[2]['payload'][:-1]+b'\x0b');assert sut.evaluate(m,rows+[conflict])['verdict']=='INCOMPLETE';checks.append('conflicting duplicate')
    assert sut.evaluate(m,rows,forensic=True)['verdict']=='INCOMPLETE';checks.append('forensic cannot pass')
    rr,ii=sut.scan(rows[0]['raw']+b'BROKEN'+b''.join(r['raw'] for r in rows[1:]),'forensic',True);assert len(rr)==len(rows) and ii;assert sut.evaluate(m,rr,ii,True)['verdict']=='INCOMPLETE';checks.append('forensic resynchronization')
    # Every truncation and single-bit mutation of all six frozen record types.
    truncated=mutated=0
    for name in ['run-start','case-start','observation','case-end','checkpoint-error','run-end']:
        golden=(ROOT/'fixtures/format-v1'/f'{name}.bin').read_bytes();sut.record(golden)
        for n in range(len(golden)):
            try:sut.record(golden[:n])
            except ValueError:truncated+=1
            else:raise AssertionError(('truncated',name,n))
        for i in range(len(golden)):
            b=bytearray(golden);b[i]^=1
            try:sut.record(b)
            except ValueError:mutated+=1
            else:raise AssertionError(('mutated',name,i))
    # CRC-correct malformed payloads cannot bypass typed validation.
    for name,kind,payload in [('zero',3,b''),('oversize',3,b'\x01\0'+bytes(1023)),('schema',3,b'\x02\0'+rows[2]['payload'][2:]),('bad-kind',3,b'\x01\0\xff'+rows[2]['payload'][3:]),('bad-utf8',4,b'\x01\0\x02\0'+U32(1)+U32(1)+U32(0)+U16(1)+bytes(2)+b'\xff')]:
        try:sut.record(envelope(kind,3,1,payload))
        except (ValueError,UnicodeError):checks.append(name)
        else:raise AssertionError(name)
    maxp=b'\x01\0\x02\0'+U16(0)+U16(0)+U16(1)+U16(1008)+U32(1)+bytes(1008);assert len(sut.record(envelope(3,3,1,maxp))['payload'])==1024;checks.append('max payload')
    # Chunks and UTF-8 are validated after concatenation.
    chunk=bytearray(rows[2]['payload']);chunk[8:10]=U16(2);bad('missing chunk',b''.join(envelope(3,3,1,bytes(chunk)) if r['sequence']==3 else r['raw'] for r in rows))
    sample=bytearray(rows[2]['payload']);sample[4:6]=U16(9);bad('unknown sample',b''.join(envelope(3,3,1,bytes(sample)) if r['sequence']==3 else r['raw'] for r in rows))
    # Snapshot validity and preservation auditing independent of the target verdict.
    snapshot=bytes.fromhex('a55a0302010605040908070c0b0a0f0e0d00f00b001004000100ff0300000000');mask=bytes([255])*20+bytes(12)
    assert sut.snapshot_checks(snapshot+snapshot+mask)==[]
    changed=bytearray(snapshot);changed[13]^=128;assert sut.snapshot_checks(snapshot+changed+mask)==[13]
    pair=b'\x01\0\x01\0'+U16(0)+U16(0)+U16(1)+U16(96)+U32(1)+snapshot+changed+mask
    bad('claimed pass with preservation failure',b''.join(envelope(3,3,1,pair) if r['sequence']==3 else r['raw'] for r in rows))
    invalid=bytearray(snapshot);invalid[26]=0
    try:sut.snapshot_checks(invalid+snapshot+mask)
    except ValueError:checks.append('unavailable masked register')
    else:raise AssertionError('invalid snapshot accepted')
    # Hashes/path containment/duplicate JSON failures on independently copied manifests.
    def reject_manifest(name,change):
        import shutil
        d=out/name;shutil.copytree(base,d);change(d)
        try:sut.manifests(d)
        except (ValueError,OSError,TypeError):checks.append(name)
        else:raise AssertionError(name)
    reject_manifest('artifact-tamper',lambda d:(d/'input.json').write_bytes(b'wrong'))
    reject_manifest('script-tamper',lambda d:(d/'selection-script.txt').write_bytes(b'changed'))
    reject_manifest('duplicate-json',lambda d:(d/'run.json').write_text('{"schema":1,"schema":1}'))
    reject_manifest('manifest-tamper',lambda d:(d/'target.json').write_text((d/'target.json').read_text().replace('7777','8888')))
    def traversal(d):
        b=json.loads((d/'bundle.json').read_text());b['artifacts'][0]['path']='../outside';h=write(d,'bundle.json',b);r=json.loads((d/'run.json').read_text());r['bundle_sha256']=h;write(d,'run.json',r)
    reject_manifest('path-traversal',traversal)
    # Dual-slot selection and independent emergency evidence, including destroyed slots.
    def slot(generation=1,state=6,used=0,confirmed=8,next_seq=9):
        b=b'MSTC'+U16(1)+U16(128)+ID+U32(generation)+U32(next_seq)+U32(confirmed)+U16(used)+bytes([state,0])+U32(0)+bytes.fromhex(m['hashes'][1]+m['hashes'][2])+bytes(12)
        return b+U32(zlib.crc32(b))+b'\xa5'+bytes(3)
    ram=bytearray(8192);ram[:128]=slot();rr,ii,c=sut.sram(ram,ID.hex(),'fixture RAM');assert not ii and c['state']==6
    emergency=envelope(5,9,0,b'\x01\0\x03\0'+U32(8)+U32(8)+U32(8));ram[0xd00:0xd3d]=emergency
    rr,ii,c=sut.sram(ram,ID.hex(),'fixture RAM');result=sut.evaluate(m,rows+rr,ii);assert result['verdict']=='INCOMPLETE' and any('checkpoint error' in x for x in result['issues']);checks.append('close error overrides complete file')
    ram[:256]=bytes(256);rr,ii,c=sut.sram(ram,ID.hex(),'destroyed slots');assert len(rr)==1 and c is None and ii;assert sut.evaluate(m,rows+rr,ii)['verdict']=='INCOMPLETE';checks.append('emergency independent of control slots')
    ram[:128]=slot(2);ram[128:256]=slot(1,state=5);rr,ii,c=sut.sram(ram,ID.hex(),'slots');assert c['state']==6;checks.append('highest generation selected')
    ram[128:256]=slot(2,state=5)
    try:sut.sram(ram,ID.hex(),'slots')
    except ValueError:checks.append('conflicting slot generations')
    else:raise AssertionError('conflicting generations accepted')
    ram[128:256]=bytes(128);ram[124]=0;rr,ii,c=sut.sram(ram,ID.hex(),'interrupted slot');assert c is None and ii;checks.append('interrupted slot rejected')
    ram[:128]=slot(3,state=4,used=len(rows[2]['raw']),confirmed=2,next_seq=4);ram[256:256+len(rows[2]['raw'])]=rows[2]['raw'];rr,ii,c=sut.sram(ram,ID.hex(),'staging');assert rr[0]['raw']==rows[2]['raw'] and ii;checks.append('staged duplicate and incomplete state')
    (out/'recovered.sram').write_bytes(ram)
    # Missing sample, wrong totals, contract hash and unsupported envelope version.
    totals=bytearray(rows[-1]['payload']);totals[4:8]=U32(99);bad('wrong totals',b''.join(r['raw'] for r in rows[:-1])+envelope(6,8,0,totals))
    contract=bytearray(rows[1]['payload']);contract[4]^=1;bad('wrong case contract',rows[0]['raw']+envelope(2,2,1,contract)+b''.join(r['raw'] for r in rows[2:]))
    header=bytearray(rows[0]['raw']);header[4]=2;header[-5:-1]=U32(zlib.crc32(header[:-5]));bad('unsupported major version',header+b''.join(r['raw'] for r in rows[1:]))
    # UTF-8 can span chunks; metadata is identical across chunks.
    chunk0=b'\x01\0\x03\0'+U16(0)+U16(0)+U16(2)+U16(1)+U32(1)+b'\xc2'
    chunk1=b'\x01\0\x03\0'+U16(0)+U16(1)+U16(2)+U16(1)+U32(1)+b'\xa3'
    chunks=rows[:2]+[sut.record(envelope(3,3,1,chunk0)),sut.record(envelope(3,4,1,chunk1))]+[sut.record(envelope(r['type'],r['sequence']+1,r['key'],r['payload'])) for r in rows[3:]]
    assert sut.evaluate(m,chunks)['verdict']=='ALL TESTS PASSED';checks.append('split UTF-8 observation')
    chunks[3]=sut.record(envelope(3,4,1,chunk1[:-1]+b'A'));assert sut.evaluate(m,chunks)['verdict']=='INCOMPLETE';checks.append('invalid concatenated UTF-8')
    def symlink_escape(d):
        (d/'input.json').unlink();(d/'input.json').symlink_to(base/'input.json')
    reject_manifest('symlink-escape',symlink_escape)
    # CLI saved text is plain even when terminal colour is explicitly enabled.
    cli=out/'cli-report';cmd=[sys.executable,str(ROOT/'scripts/report_results.py'),'--run',str(base),'--output',str(cli),'--colour','always'];result=subprocess.run(cmd,capture_output=True,text=True);assert result.returncode==0,result.stderr;assert '\x1b[97;42m' in result.stdout and '\x1b' not in (cli/'summary.txt').read_text();assert subprocess.run(cmd,capture_output=True).returncode!=0;checks.append('CLI colour/plain and no overwrite')
    for scenario,exit_code in [('two-assertions-one-test',1),('missing-finalization',2),('skipped',3),('empty-plan',2)]:
        dest=out/('cli-'+scenario);r=subprocess.run([sys.executable,str(ROOT/'scripts/report_results.py'),'--run',str(out/scenario),'--output',str(dest),'--colour','never'],capture_output=True,text=True);assert r.returncode==exit_code,(scenario,r.stdout,r.stderr);assert '\x1b' not in r.stdout;checks.append('CLI '+scenario)
    r=subprocess.run([sys.executable,str(ROOT/'scripts/report_results.py'),'--run',str(base),'--output',str(out/'cli-recovered'),'--sram',str(out/'recovered.sram'),'--recovery-note','synthetic dump for qualification; no hardware acquisition'],capture_output=True,text=True);assert r.returncode==2 and 'INCOMPLETE' in r.stdout;checks.append('CLI recovered SRAM provenance')
    report=sut.evaluate(m,rows);report['issues']=['untrusted\x1b[31mtext\nnext'];assert '\x1b' not in sut.render(report);checks.append('untrusted terminal controls escaped')
    result=dict(passed=True,checks=checks,report_oracles=len(oracles),truncations=truncated,mutations=mutated)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASSED:',len(checks),'decoder/report scenarios;',truncated,'truncations;',mutated,'corruptions rejected.')
if __name__=='__main__':main()
