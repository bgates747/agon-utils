#!/usr/bin/env python3
"""Create generic writer fixtures and test the bounded C++ consumer."""
from pathlib import Path
import json
import os
import struct
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'api'))
from buffers import BufferRecord,build_container,read_container
BUILD=HERE/'build'

def main():
    BUILD.mkdir(exist_ok=True)
    sizes=(1,8191,8192,8193,65535,65536,160000,200000)
    good=build_container([BufferRecord(i,bytes((17+i,))*n) for i,n in enumerate(sizes)])
    (BUILD/'large.agnb').write_bytes(good)
    base=build_container([BufferRecord(12,b'Z'*7)])
    def mutate(name,at,raw):
        data=bytearray(base);data[at:at+len(raw)]=raw;(BUILD/(name+'.agnb')).write_bytes(data)
    mutate('id',44,b'\xff\xff');mutate('raw',56,b'\1');mutate('version',21,b'\4')
    mutate('order',36,b'RAWD');mutate('bounds',28,b'\xff'*4);mutate('size',64,b'\0'*4)
    mutate('pad',len(base)-1,b'\1');mutate('vers-pad',22,b'\1');mutate('bhdr-size',40,struct.pack('<I',1))
    mutate('riff-overflow',4,b'\xff'*4)
    (BUILD/'truncated.agnb').write_bytes(base[:-1]);(BUILD/'trailing.agnb').write_bytes(base+b'x')
    def combine(second):
        raw=base+second[24:];return raw[:4]+struct.pack('<I',len(raw)-8)+raw[8:]
    second=build_container([BufferRecord(12,b'Q'*5)])
    (BUILD/'duplicate.agnb').write_bytes(combine(second))
    bad=bytearray(second);bad[56]=1;(BUILD/'late.agnb').write_bytes(combine(bad))
    assert len(read_container((BUILD/'duplicate.agnb').read_bytes()))==2
    command=[os.environ.get('CXX','c++'),'-std=c++17','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined',HERE/'host_checks.cpp','-o',BUILD/'checks']
    subprocess.run(list(map(str,command)),check=True)
    result=subprocess.run([str(BUILD/'checks'),str(BUILD)],check=True,text=True,capture_output=True)
    print(result.stdout,end='')
    (HERE/'host-evidence.json').write_text(json.dumps({'passed':True,'summary':result.stdout.strip(),'container_bytes':len(good),'payload_bytes':sum(sizes),'workspace_bytes':8192,'sanitizers':['address','undefined']},indent=2)+'\n')
if __name__=='__main__':main()
