#!/usr/bin/env python3
"""Build/run a dedicated stock-MOS plain-buffer loader qualification profile."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import signal
import struct
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
AGNB=HERE.parents[2]
ROOT=AGNB.parents[1]
BUILD=HERE/'build'
PROFILE=AGNB/'.emulator'
sys.path.insert(0,str(AGNB/'api'))
from buffers import BufferRecord,build_container


def prepare(runtime,assembler):
    BUILD.mkdir(exist_ok=True)
    spec=importlib.util.spec_from_file_location('canonical',ROOT.parent/'agon-dev-env/scripts/setup_emulator.py')
    canonical=importlib.util.module_from_spec(spec);spec.loader.exec_module(canonical)
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if str(PROFILE/'sdcard').encode() in (proc/'cmdline').read_bytes().split(b'\0'):
                raise RuntimeError('Close the AGNB profile before preparing it')
        except OSError:pass
    if PROFILE.exists() and not (PROFILE/'.agnb-001').exists():
        raise RuntimeError('Refusing an unowned existing profile')
    sd=canonical.link_shared_runtime(PROFILE,runtime)
    (PROFILE/'.agnb-001').write_text('AGNB-001 plain-buffer qualification\n')
    app=sd/'agnb';app.mkdir(exist_ok=True)
    sizes=(1,8191,8192,8193,65535,65536,160000,200000)
    records=[BufferRecord(5000+i,bytes((17+i,))*n) for i,n in enumerate(sizes)]
    (app/'large.agnb').write_bytes(build_container(records))
    (app/'again.agnb').write_bytes(build_container([BufferRecord(5001,b'Q'*9001)]))
    bad=bytearray(build_container([BufferRecord(5002,b'x')]))
    bad[44:46]=b'\xff\xff';(app/'bad-id.agnb').write_bytes(bad)
    bad=bytearray(build_container([BufferRecord(5002,b'x')]))
    bad[56]=1;(app/'bad-raw.agnb').write_bytes(bad)
    good=build_container([BufferRecord(5010,b'Z'*7)])
    bad=bytearray(build_container([BufferRecord(5011,b'x')]))
    bad[56]=1
    combined=good+bad[24:];combined=combined[:4]+struct.pack('<I',len(combined)-8)+combined[8:]
    (app/'late.agnb').write_bytes(combined)
    (app/'truncated.agnb').write_bytes(good[:-1])
    if assembler is not None:
        subprocess.run([str(assembler),'guest.asm','build/probe.bin','-c'],cwd=HERE,check=True)
    elif not (BUILD/'probe.bin').exists():
        raise RuntimeError('Supply --assembler or a preassembled build/probe.bin')
    (app/'probe.bin').write_bytes((BUILD/'probe.bin').read_bytes())
    (app/'results.dat').unlink(missing_ok=True)
    (sd/'autoexec.txt').write_bytes(b'SET KEYBOARD 1\r\ncd /agnb\r\nload probe.bin\r\nrun .\r\n')
    canonical.write_profile_launcher(PROFILE)
    names=['fab-agon-emulator','fab-agon-emulator.bin','firmware/vdp_platform.so','mos_platform.bin','mos_platform.map',
           'sdcard/autoexec.txt']+['sdcard/agnb/'+p.name for p in app.iterdir() if p.name!='results.dat']
    pins={n:hashlib.sha256((PROFILE/n).read_bytes()).hexdigest() for n in names}
    (PROFILE/'.runtime.sha256').write_text(''.join(value+'  '+name+'\n' for name,value in pins.items()))
    def observation(id,size,value):
        return struct.pack('<H',id)+size.to_bytes(3,'little')+bytes((value,))
    expected=b''.join(observation(r.buffer_id,len(r.data),r.data[0]) for r in records)+b'\0'
    expected+=observation(5001,9001,ord('Q'))+bytes((0,9,10))
    expected+=observation(5010,7,ord('Z'))+bytes((10,8))
    (BUILD/'expected.dat').write_bytes(expected)
    metadata={'container_bytes':(app/'large.agnb').stat().st_size,'aggregate_payload_bytes':sum(sizes),
              'app_bytes':(app/'probe.bin').stat().st_size,'transfer_window_bytes':8192,'expected_bytes':len(expected),'pins':pins}
    (BUILD/'profile.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata


def execute(meta):
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for key in ('LD_PRELOAD','BASH_ENV'):env.pop(key,None)
    result=PROFILE/'sdcard/agnb/results.dat';start=time.monotonic()
    with (BUILD/'emulator.log').open('w') as log:
        process=subprocess.Popen(['./fab-agon-emulator','--renderer','sw'],cwd=PROFILE,env=env,
                                 stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while not result.exists() or result.stat().st_size<meta['expected_bytes']:
                if process.poll() is not None:raise RuntimeError('Emulator exited before results')
                if time.monotonic()-start>180:raise TimeoutError('Inspect build/emulator.log')
                time.sleep(.05)
        finally:
            if process.poll() is None:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    actual=result.read_bytes();expected=(BUILD/'expected.dat').read_bytes()
    assert actual==expected,(actual.hex(),expected.hex())
    subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=PROFILE,check=True)
    report=dict(meta,passed=True,elapsed_seconds=round(time.monotonic()-start,3),host=os.uname().nodename,
                scope='actual stock Fab/MOS loader, explicit IDs, payload samples, multi-window, consecutive load, metadata/late/truncation errors',
                graphical_launch=False,physical=False,human_review='pending')
    (HERE/'target-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Stock AGNB qualification passes:',report['elapsed_seconds'],'seconds',flush=True)
    result.unlink() # Human review must produce a fresh result after its next launch.


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,required=True);p.add_argument('--assembler',type=Path)
    p.add_argument('--stage-only',action='store_true');a=p.parse_args()
    m=prepare(a.runtime.resolve(),a.assembler.resolve() if a.assembler else None)
    if not a.stage_only:execute(m)
