from pathlib import Path
import os,pty,subprocess,select,time,re,json,hashlib,argparse
W=Path(__file__).resolve().parent;P=W.parents[3]
parser=argparse.ArgumentParser();parser.add_argument("--image",type=Path,default=P/".emulator/w05-basic.img");args=parser.parse_args()
assert hashlib.sha256((W/"bbc-basic-v-adl.bin").read_bytes()).hexdigest()=="ed6ff5a4707f941ff7b178111771a0bfade3ecdefccbb3bcb4015b9a6d5a87ab"
raw=bytearray();ansi=re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")
master,slave=pty.openpty();proc=subprocess.Popen([str(P.parents[1]/".venv/bin/python"),str(P/"scripts/run_emulator.py"),"--image",str(args.image.resolve()),"-d","-b","0"],stdin=slave,stdout=slave,stderr=slave,start_new_session=True);os.close(slave)
def wait(offset):
 end=time.monotonic()+30
 while time.monotonic()<end:
  if b">> " in ansi.sub(b"",bytes(raw[offset:])):return
  if select.select([master],[],[],.1)[0]:raw.extend(os.read(master,65536))
  if proc.poll() is not None:raise RuntimeError("Emulator exited")
 raise TimeoutError("No expected checkpoint in 30 seconds")
def command(c):
 offset=len(raw);os.write(master,(c+"\n").encode());wait(offset)
try:
 wait(0)
 for c in ['trigger $10 state','break $400d3','delete $0','c','state','s','state']:
  command(c)
 os.write(master,b'exit\n');proc.wait(timeout=5)
 text=ansi.sub(b"",bytes(raw)).decode(errors="replace")
 states=re.findall(r'\* ([0-9a-f]{6}):([^\r\n]*)',text)
 output=bytes(int(re.search(r'AF:([0-9a-f]{2})',s)[1],16) for pc,s in states if int(pc,16)==0x10)
 assert output == b'W05 BASIC PASS\r\n',repr(output)
 assert b'W05 BASIC FAIL' not in output
 assert any(int(pc,16)==0x400d3 and 'HL:000000' in s for pc,s in states)
 lastpc,last=states[-1];assert int(lastpc,16)<0x20000 and 'HL:000000' in last,(lastpc,last)
 (W/'captured-output.bin').write_bytes(output)
 result=dict(passed=True,interpreter='bbc-basic-v-adl.bin',version='v1.0RC1',sha256=hashlib.sha256((W/'bbc-basic-v-adl.bin').read_bytes()).hexdigest(),returned_to_mos_pc=lastpc,hl=0,backend='mbr-fat32-image',emulator_exit=proc.returncode)
 (W/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(repr(output));print(result)
finally:
 if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
 os.close(master);(W/'debugger.raw.txt').write_bytes(raw);(W/'debugger.txt').write_bytes(ansi.sub(b"",bytes(raw)))
