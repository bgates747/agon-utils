from pathlib import Path
import os,pty,subprocess,select,time,re
W=Path(__file__).resolve().parent
P=W.parents[4]
raw=bytearray();ansi=re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")
m,s=pty.openpty()
proc=subprocess.Popen([str(P.parents[1]/".venv/bin/python"),str(P/"scripts/run_emulator.py"),"--image",str(P/".emulator/w06-trial-cpp.img"),"-d","-b","0"],stdin=s,stdout=s,stderr=s,start_new_session=True);os.close(s)
def wait(offset):
 end=time.monotonic()+30
 while time.monotonic()<end:
  if b">> " in ansi.sub(b"",bytes(raw[offset:])):return
  if select.select([m],[],[],.1)[0]:raw.extend(os.read(m,65536))
  if proc.poll() is not None:raise RuntimeError("Exited")
 raise TimeoutError("Checkpoint timeout")
def command(c):
 offset=len(raw);os.write(m,(c+"\n").encode());wait(offset)
try:
 wait(0)
 for c in ['trigger $387b "OBEY ENTRY" : state : mem sp 48','trigger $e674 "F_OPEN" : state : mem sp 24','break $3be5','delete $0','c','state','mem sp 96','mem ix 48','mem $1a263 96','dis24 $3bba $3c04','dis24 $f3ec $f410','dis24 $f4fd $f51a','dis24 $1d70 $1da0','delete $3be5','c','state','mem $bff5f 144']:
  command(c)
 os.write(m,b'exit\n');proc.wait(timeout=5)
finally:
 if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
 os.close(m);(W/'debugger.raw.txt').write_bytes(raw);(W/'debugger.txt').write_bytes(ansi.sub(b"",bytes(raw)))
 print(ansi.sub(b"",bytes(raw)).decode(errors='replace')[-15000:])
