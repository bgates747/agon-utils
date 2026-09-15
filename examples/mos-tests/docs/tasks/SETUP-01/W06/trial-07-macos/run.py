from pathlib import Path
import os,pty,subprocess,select,time,re,json
p=Path(__file__).resolve().parent
m,s=pty.openpty();env=os.environ.copy();env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
proc=subprocess.Popen(['./fab-agon-emulator','--renderer','sw','-d','-b','0'],cwd=p,env=env,stdin=s,stdout=s,stderr=s,start_new_session=True);os.close(s)
raw=bytearray();ansi=re.compile(rb'\x1b\[[0-?]*[ -/]*[@-~]')
def prompt(offset):
 end=time.monotonic()+30
 while time.monotonic()<end:
  if b'>> ' in ansi.sub(b'',bytes(raw[offset:])):return
  if select.select([m],[],[],.1)[0]:raw.extend(os.read(m,65536))
  if proc.poll() is not None:raise RuntimeError('Emulator exited')
 raise TimeoutError('No prompt within 30 seconds')
try:
 prompt(0)
 for cmd in ['trigger $401e1 state','trigger $10 state','trigger $400c8 pause : state','delete $0','c']:
  offset=len(raw);os.write(m,(cmd+'\n').encode());prompt(offset)
 os.write(m,b'exit\n');proc.wait(timeout=5)
finally:
 if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
 os.close(m);(p/'debugger.raw.txt').write_bytes(raw)
 clean=ansi.sub(b'',bytes(raw));(p/'debugger.txt').write_bytes(clean)
 print(clean.decode(errors='replace')[-4000:]);print('Process exit:',proc.returncode)
