"""Validate v1 evidence and render a summary-first report; never repairs evidence."""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,re,struct,sys,zlib
from plan_run import pairs
NAMES=['PASSED','FAILED','OBSERVED','SKIPPED','UNSUPPORTED','BLOCKED','ERROR','INCOMPLETE']
def require(ok,message):
    if not ok:raise ValueError(message)
def uint(v,bits=32):return type(v)is int and 0<=v<2**bits
def hx(v,n=64):return isinstance(v,str) and re.fullmatch('[0-9a-f]{%d}'%n,v) is not None
def sha(b):return hashlib.sha256(b).hexdigest()
def u16(b,o=0):return int.from_bytes(b[o:o+2],'little')
def u32(b,o=0):return int.from_bytes(b[o:o+4],'little')
def text(b):return b.decode('utf-8',errors='strict')
def safe(s):return ''.join(c if c.isprintable() or c==' ' else '\\x%02x'%ord(c) for c in str(s))
def fields(o,names):require(isinstance(o,dict) and set(o)==set(names.split()),'invalid manifest fields')
def jsonfile(root,name,names):
    b=(root/name).read_bytes();o=json.loads(b.decode('utf-8'),object_pairs_hook=pairs);fields(o,names);require(type(o['schema'])is int and o['schema']==1,'unsupported manifest version');return o,sha(b)
def manifests(root):
    cat,ch=jsonfile(root,'catalogue.json','schema cases')
    plan,ph=jsonfile(root,'plan.json','schema catalogue_sha256 selectors case_keys backend capabilities script_sha256')
    target,th=jsonfile(root,'target.json','schema backend declared_by mos_binary_sha256 mos_map_sha256 toolchain_manifest_sha256 emulator_binary_sha256 vdp_binary_sha256')
    bundle,bh=jsonfile(root,'bundle.json','schema catalogue_sha256 artifacts')
    run,rh=jsonfile(root,'run.json','schema run_id parent_run_id bundle_sha256 catalogue_sha256 plan_sha256 target_sha256')
    require(hx(run['run_id'],32) and int(run['run_id'],16)!=0,'invalid run identity')
    require(run['parent_run_id'] is None or (hx(run['parent_run_id'],32) and int(run['parent_run_id'],16)!=0 and run['parent_run_id']!=run['run_id']),'invalid parent identity')
    require([run[k] for k in ['bundle_sha256','catalogue_sha256','plan_sha256','target_sha256']]==[bh,ch,ph,th],'manifest identity mismatch')
    require(plan['catalogue_sha256']==bundle['catalogue_sha256']==ch,'catalogue identity mismatch')
    require(plan['backend']==target['backend'] and target['backend'] in ['hardware','emulator'],'backend mismatch')
    require(isinstance(target['declared_by'],str) and bool(target['declared_by']),'missing target provenance')
    for k in ['mos_binary_sha256','mos_map_sha256','toolchain_manifest_sha256','emulator_binary_sha256','vdp_binary_sha256']:
        v=target[k];require(hx(v) or (target['backend']=='hardware' and k in ['mos_map_sha256','emulator_binary_sha256','vdp_binary_sha256'] and v is None),'invalid target hash '+k)
    require(isinstance(bundle['artifacts'],list),'invalid artifacts');paths=set();hashes=set()
    for a in bundle['artifacts']:
        fields(a,'path size sha256');name=a['path'];require(isinstance(name,str) and name and '\\' not in name,'invalid artifact path')
        parts=PurePosixPath(name);require(not parts.is_absolute() and all(x not in ['.','..'] for x in name.split('/')) and name not in paths,'unsafe/duplicate artifact path')
        f=(root/name).resolve();require(f.is_relative_to(root.resolve()),'artifact escapes root')
        require(uint(a['size']) and hx(a['sha256']),'invalid artifact metadata');data=f.read_bytes();require(len(data)==a['size'] and sha(data)==a['sha256'],'artifact mismatch '+name);paths.add(name);hashes.add(a['sha256'])
    require(isinstance(cat['cases'],list) and cat['cases'],'empty catalogue');cases={};ids=set();caps=set()
    for c in cat['cases']:
        fields(c,'key id function route group expectation_sha256 fixture_sha256 capabilities isolation samples timeout_ms')
        require(uint(c['key']) and c['key'] and c['key'] not in cases,'invalid/duplicate case key')
        for k in ['id','function','group']:require(isinstance(c[k],str) and re.fullmatch(r'[A-Za-z0-9._-]+',c[k]),'invalid case identifier')
        require(c['id'] not in ids,'duplicate case ID');ids.add(c['id'])
        require(c['route'] in ['rst08','c-function','rst','synthetic'] and c['isolation'] in ['pure','stateful','media','exclusive','control'],'invalid case route/isolation')
        require(isinstance(c['capabilities'],list) and all(isinstance(x,str) and re.fullmatch(r'[A-Za-z0-9._-]+',x) for x in c['capabilities']) and len(set(c['capabilities']))==len(c['capabilities']),'invalid capabilities');caps.update(c['capabilities'])
        require(isinstance(c['samples'],list) and c['samples'] and all(uint(x,16) for x in c['samples']) and len(set(c['samples']))==len(c['samples']),'invalid samples')
        require(uint(c['timeout_ms']) and c['timeout_ms']>0,'invalid timeout')
        require(all(hx(c[k]) and c[k] in hashes for k in ['fixture_sha256','expectation_sha256']),'missing fixture/expectation artifact');cases[c['key']]=c
    keys=plan['case_keys'];require(isinstance(keys,list) and keys and all(uint(k) and k in cases for k in keys) and len(set(keys))==len(keys),'empty/unknown/duplicate selected keys')
    require(isinstance(plan['capabilities'],list) and all(isinstance(x,str) and x in caps for x in plan['capabilities']) and len(set(plan['capabilities']))==len(plan['capabilities']),'unknown plan capability')
    require(isinstance(plan['selectors'],list) and plan['selectors'] and all(isinstance(s,str) for s in plan['selectors']),'invalid selectors')
    selected=set()
    for s in plan['selectors']:
        matches=[k for k,c in cases.items() if s=='all' or any(s==prefix+ c[field] for prefix,field in [('case:','id'),('function:','function'),('group:','group')])]
        require(matches,'unknown selector '+s);selected.update(matches)
    require(keys==[k for k in cases if k in selected],'selection order/membership mismatch')
    require(hx(plan['script_sha256']) and sha((root/'selection-script.txt').read_bytes())==plan['script_sha256'],'script identity mismatch')
    return dict(cases=cases,keys=keys,run=run,plan=plan,target=target,hashes=[bh,ch,ph,th],manifest_sha256=rh)

def record(data,offset=0):
    require(len(data)-offset>=40,'truncated header');h=data[offset:offset+40];n=u32(h,32)
    require(h[:4]==b'MSTR' and h[4]==1 and 1<=h[5]<=6 and u16(h,6)==40 and h[36:]==bytes(4),'invalid header/version')
    require(2<=n<=1024,'invalid payload length');raw=data[offset:offset+45+n];require(len(raw)==45+n,'truncated record')
    require(raw[-1]==0xa5,'missing commit');require(u32(raw,len(raw)-5)==zlib.crc32(raw[:-5]),'CRC mismatch')
    require(any(h[8:24]) and u32(h,24)>0,'invalid record identity/sequence');p=raw[40:-5];require(p[:2]==b'\x01\0','unsupported payload version')
    t=h[5];r=dict(type=t,sequence=u32(h,24),key=u32(h,28),run=h[8:24].hex(),raw=raw,payload=p)
    if t==1:require(n==136 and p[2] in [1,2] and not p[3] and u32(p,4)>0 and not r['key'],'invalid run start')
    elif t==2:require(n==68 and u16(p,2)>0 and r['key']>0,'invalid case start')
    elif t==3:
        require(n>=16 and p[2] in [1,2,3] and not p[3] and u16(p,8)>0 and u16(p,6)<u16(p,8) and u16(p,10)==n-16 and u32(p,12)>0 and r['key']>0,'invalid observation')
        require(p[2]!=1 or (n==112 and u16(p,6)==0 and u16(p,8)==1),'invalid register pair')
    elif t==4:
        require(n>=20 and 1<=p[2]<=8 and not p[3] and not u16(p,18) and u16(p,16)==n-20 and r['key']>0,'invalid case end')
        a,f,o=u32(p,4),u32(p,8),u32(p,12);reason=text(p[20:]);d=p[2]
        require(f<=a and (d==1 or bool(reason)),'invalid reason/counts')
        require(d!=1 or (a>0 and f==0),'invalid pass');require(d!=2 or f>0,'invalid failure')
        require(d not in [3,4,5,6] or (a==f==0 and (d==3 or o==0)),'invalid limited disposition')
        r.update(outcome=NAMES[d-1],assertions=a,failed_assertions=f,observations=o,reason=reason)
    elif t==5:require(n==16 and 1<=p[2]<=5 and not p[3],'invalid checkpoint error')
    else:require(n==68 and p[2:4]==bytes(2) and not r['key'],'invalid run end')
    return r

def scan(data,label,forensic=False):
    rows=[];issues=[];offset=0;last=0
    while offset<len(data):
        try:
            r=record(data,offset)
            require(r['sequence']>=last,'reordered source sequences');last=r['sequence'];r['source']=label;r['offset']=offset;rows.append(r);offset+=len(r['raw'])
        except (ValueError,UnicodeError) as e:
            issues.append(f'{label} at byte {offset}: {e}')
            if not forensic:break
            found=data.find(b'MSTR',offset+1)
            if found<0:break
            offset=found
    return rows,issues

def sram(data,run,label):
    require(len(data)==8192,'SRAM dump must be exactly 8192 bytes');valid=[];issues=[]
    for off in [0,128]:
        b=data[off:off+128]
        if b[124]!=0xa5:continue
        if not (b[:8]==b'MSTC\x01\0\x80\0' and not b[39] and b[108:120]==bytes(12) and b[125:]==bytes(3) and u32(b,120)==zlib.crc32(b[:120])):continue
        require(b[8:24].hex()==run,'foreign-run SRAM slot')
        require(u32(b,24)>0 and u32(b,28)>u32(b,32) and u16(b,36)<=2048 and 1<=b[38]<=6,'invalid SRAM control bounds')
        valid.append(b)
    if not valid:
        rows=[];issues.append(label+': no valid control slot; staging extent unavailable')
        if data[0xd3c]==0xa5:
            try:
                r=record(data[0xd00:0xd3d]);require(r['type']==5,'invalid emergency type');r.update(source=label+':emergency',offset=0xd00);rows.append(r)
            except ValueError as e:issues.append(label+': '+str(e))
        return rows,issues,None
    if len(valid)==2 and u32(valid[0],24)==u32(valid[1],24):require(valid[0]==valid[1],'conflicting SRAM generations')
    b=max(valid,key=lambda x:u32(x,24));used=u16(b,36)
    rows,errors=scan(data[256:256+used],label+':staging');issues+=errors
    # A stopped/I/O/unfinished state is explicit limited completion evidence.
    if b[38]!=6:issues.append(label+': SRAM state is not ended')
    elif used or u32(b,40) or u32(b,28)!=u32(b,32)+1:issues.append(label+': inconsistent ended SRAM control')
    if data[0xd3c]==0xa5:
        try:r=record(data[0xd00:0xd3d]);require(r['type']==5,'invalid emergency type');r.update(source=label+':emergency',offset=0xd00);rows.append(r)
        except ValueError as e:issues.append(label+': '+str(e))
    return rows,issues,dict(state=b[38],confirmed=u32(b,32),next=u32(b,28),catalogue=b[44:76].hex(),plan=b[76:108].hex())

def snapshot_checks(data):
    a,b,mask=data[:32],data[32:64],data[64:];require(len(data)==96,'register pair length')
    require(mask[20:23]==bytes(3) and mask[26:]==bytes(6) and not(mask[24]&254 or mask[25]&254),'invalid preservation mask')
    fields_=[(0,2),(2,3),(5,3),(8,3),(11,3),(14,3),(17,3),(20,3),(23,1),(24,1),(25,1)]
    for snap in [a,b]:
        bits=u16(snap,26);require(not(bits&0xf800) and snap[28:]==bytes(4) and snap[24] in [0,1] and snap[25] in [0,1],'invalid snapshot')
        for bit,(off,n) in enumerate(fields_):
            if not bits&(1<<bit):require(snap[off:off+n]==bytes(n) and mask[off:off+n]==bytes(n),'unavailable masked register')
    return [i for i in range(26) if (a[i]^b[i])&mask[i]]

def evaluate(m,rows,issues=(),forensic=False):
    problems=list(issues);ends={};observations={};byseq={};runstart=False;runend=False;active=None;started=[];diffs={}
    def problem(s):problems.append(s)
    for r in rows:
        if r['run']!=m['run']['run_id']:problem('foreign-run record');continue
        seq=r['sequence']
        if seq in byseq:
            if byseq[seq]['raw']!=r['raw']:problem('conflicting sequence '+str(seq))
        else:byseq[seq]=r
    for expected,(seq,r) in enumerate(sorted(byseq.items()),1):
        if seq!=expected:problem('missing record sequence before '+str(seq))
        t,k,p=r['type'],r['key'],r['payload']
        try:
            if t==5:problem('checkpoint error: operation %d, status %d, attempted %d, confirmed %d'%(p[2],u32(p,4),u32(p,8),u32(p,12)));continue
            require(not runend,'records after run end')
            if t==1:
                require(not runstart and seq==1 and not started,'unexpected run start');runstart=True
                require(p[2]==(1 if m['plan']['backend']=='emulator' else 2) and u32(p,4)==len(m['keys']),'run selection/backend mismatch')
                require([p[o:o+32].hex() for o in [8,40,72,104]]==m['hashes'],'run manifest hashes mismatch')
                continue
            require(runstart,'missing run start')
            if t==6:
                require(active is None,'run ended inside case');require(p[36:68].hex()==m['hashes'][2],'run-end plan mismatch');runend=True
                counts=[sum(e['outcome']==name for e in ends.values()) for name in NAMES]
                require(counts==[u32(p,4+i*4) for i in range(8)],'run-end totals mismatch');continue
            require(k in m['keys'],'unknown/unselected case key');c=m['cases'][k]
            if t==2:
                require(active is None and k not in started,'overlapping/duplicate case start');require(len(started)<len(m['keys']) and k==m['keys'][len(started)],'case order mismatch')
                active=k;started.append(k);observations[k]={};diffs[k]=[]
                require(u16(p,2)==len(c['samples']) and p[4:36].hex()==c['fixture_sha256'] and p[36:].hex()==c['expectation_sha256'],'case contract mismatch')
            elif t==3:
                require(active==k,'observation outside active case');sample,chunk,count,oid=u16(p,4),u16(p,6),u16(p,8),u32(p,12)
                require(sample in c['samples'],'unknown sample');key=(sample,oid);obs=observations[k].setdefault(key,dict(kind=p[2],count=count,chunks={}))
                require(obs['kind']==p[2] and obs['count']==count and chunk not in obs['chunks'],'conflicting/duplicate observation chunk');obs['chunks'][chunk]=p[16:]
                if p[2]==1:diffs[k]+=snapshot_checks(p[16:])
            elif t==4:
                require(active==k and k not in ends,'case end outside active case');obs=observations[k]
                for item in obs.values():
                    require(len(item['chunks'])==item['count'] and sorted(item['chunks'])==list(range(item['count'])),'missing observation chunks')
                    if item['kind']==3:text(b''.join(item['chunks'][i] for i in range(item['count'])))
                require(r['observations']==len(obs),'observation count mismatch')
                if r['outcome'] in ['PASSED','FAILED','OBSERVED']:require({s for s,_ in obs}==set(c['samples']),'missing sample evidence')
                if r['outcome']=='PASSED':require(not diffs[k],'preserved-register difference in claimed pass');require(set(c['capabilities'])<=set(m['plan']['capabilities']),'pass lacks required capability')
                ends[k]=r;active=None
        except (ValueError,UnicodeError) as e:problem('sequence %d: %s'%(seq,e))
    if not runstart:problem('missing run start')
    if not runend:problem('missing run end')
    if active is not None:problem('unfinished case '+str(active))
    if set(ends)!=set(m['keys']):problem('selected cases lack valid completion')
    if any(e['outcome'] in ['ERROR','INCOMPLETE'] for e in ends.values()):problem('case infrastructure error/incomplete')
    if forensic:problem('forensic fragments cannot establish completion')
    counts={name:sum(e['outcome']==name for e in ends.values()) for name in NAMES};failed=[m['cases'][k]['id'] for k in m['keys'] if k in ends and ends[k]['outcome']=='FAILED']
    verdict='INCOMPLETE' if problems else 'FAILURES' if failed else 'ALL TESTS PASSED' if counts['PASSED']==len(m['keys']) else 'NO FAILURES OBSERVED — coverage limited'
    details=[]
    for k in m['keys']:
        if k not in ends:continue
        e=ends[k]
        if e['outcome']=='PASSED':continue
        details.append(dict(id=m['cases'][k]['id'],function=m['cases'][k]['function'],outcome=e['outcome'],assertions=e['assertions'],failed_assertions=e['failed_assertions'],reason=e['reason'],preservation_changed_offsets=diffs.get(k,[]),observations=[dict(sample=s,id=oid,kind=o['kind'],chunks=[v.hex() for _,v in sorted(o['chunks'].items())]) for (s,oid),o in observations.get(k,{}).items()]))
    return dict(verdict=verdict,selected=len(m['keys']),counts=counts,failed_tests=len(failed),failed_ids=failed,issues=problems,details=details,run_id=m['run']['run_id'],backend=m['plan']['backend'])

def render(report,colour=False):
    def badge(word):return ('\x1b[97;42m'+word+'\x1b[0m') if colour and word=='PASSED' else ('\x1b[97;41m'+word+'\x1b[0m') if colour and word=='FAILED' else word
    verdict=report['verdict'];headline=badge('PASSED')+': ALL TESTS PASSED' if verdict=='ALL TESTS PASSED' else badge('FAILED')+': '+str(report['failed_tests'])+(' test failed' if report['failed_tests']==1 else ' tests failed') if verdict=='FAILURES' else verdict
    lines=[headline,f"Selected: {report['selected']}; passed: {report['counts']['PASSED']}; failed tests: {report['failed_tests']}."]
    if report['failed_ids']:lines.append('Failed tests: '+', '.join(map(safe,report['failed_ids'])))
    lines+=['Backend: '+safe(report['backend'])+'. Verdict concerns supplied evidence; hardware and close/power-loss durability are not inferred.']
    if report['issues']:lines+=['','Evidence problems:']+['- '+safe(i) for i in report['issues']]
    if report['details']:
        lines+=['','Case details (non-passing cases):']
        for d in report['details']:
            lines.append(badge(d['outcome'])+': '+safe(d['id'])+' ('+safe(d['function'])+') — '+safe(d['reason']))
            lines.append('  Assertions: %d; failed: %d.'%(d['assertions'],d['failed_assertions']))
            if d['preservation_changed_offsets']:lines.append('  Preserved register bytes changed: '+str(d['preservation_changed_offsets']))
            for o in d['observations']:lines.append('  Sample %d, observation %d, kind %d: %s'%(o['sample'],o['id'],o['kind'],' '.join(o['chunks'])))
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--records',type=Path);ap.add_argument('--recovered',action='append',default=[],type=Path);ap.add_argument('--sram',type=Path);ap.add_argument('--recovery-note');ap.add_argument('--forensic',action='store_true');ap.add_argument('--colour',choices=['auto','always','never'],default='auto');a=ap.parse_args()
    if (a.recovered or a.sram or a.forensic) and not a.recovery_note:ap.error('recovery requires --recovery-note describing source/backend and acquisition before reset')
    a.output.mkdir(parents=True,exist_ok=False);sources=[];rows=[]
    try:
        m=manifests(a.run);rows=[];issues=[]
        for path in [a.records or a.run/'results.bin',*a.recovered]:
            if path==a.run/'results.bin' and not path.exists() and (a.sram or a.recovered):
                issues.append('card results unavailable; recovery evidence only');continue
            data=path.read_bytes();sources.append(dict(path=str(path.resolve()),sha256=sha(data)));r,e=scan(data,str(path),a.forensic);rows+=r;issues+=e
        if a.sram:
            data=a.sram.read_bytes();sources.append(dict(path=str(a.sram.resolve()),sha256=sha(data)));r,e,control=sram(data,m['run']['run_id'],str(a.sram));rows+=r;issues+=e
            if control:
                require(control['catalogue']==m['hashes'][1] and control['plan']==m['hashes'][2],'SRAM manifest mismatch')
                last=max([r['sequence'] for r in rows],default=0)
                if control['confirmed']>last:issues.append('SRAM claims confirmation beyond supplied evidence')
                if control['state']==6 and (control['confirmed']!=last or control['next']!=last+1):issues.append('ended SRAM progress disagrees with supplied evidence')
        report=evaluate(m,rows,issues,a.forensic)
    except (OSError,ValueError,KeyError,TypeError,UnicodeError) as e:
        report=dict(verdict='CONFIGURATION ERROR',selected=0,counts={n:0 for n in NAMES},failed_tests=0,failed_ids=[],issues=[str(e)],details=[],backend='unverified')
    report.update(sources=sources,recovery_note=a.recovery_note,forensic=a.forensic)
    decoded=[{k:(v.hex() if isinstance(v,bytes) else v) for k,v in r.items() if k!='raw'} for r in rows]
    (a.output/'decoded-records.json').write_text(json.dumps(decoded,indent=2)+'\n')
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');(a.output/'summary.txt').write_text(render(report))
    print(render(report,a.colour=='always' or a.colour=='auto' and sys.stdout.isatty()),end='')
    return 0 if report['verdict']=='ALL TESTS PASSED' else 1 if report['verdict']=='FAILURES' else 3 if report['verdict'].startswith('NO FAILURES') else 2
if __name__=='__main__':sys.exit(main())
