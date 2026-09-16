"""Archive W03 qualification evidence without disposable full-card images."""
from pathlib import Path
import hashlib,json,subprocess,tarfile
ROOT=Path.cwd();dest=ROOT/'docs/tasks/MAIN-05/W03';runtime=ROOT/'.emulator/disposition'
symlinks={str(p.relative_to(ROOT)):str(p.readlink()) for p in runtime.rglob('*') if p.is_symlink()}
files=[p for p in runtime.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix!='.img' and '__pycache__' not in p.parts]
sources=[]
for folder in ['apps/startup-runner','scripts','agents','tests/disposition','tests/recovery']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and (p.suffix in {'.h','.cpp','.asm','.py'} or p.name=='Makefile') and 'build' not in p.parts:sources.append(p)
sources+=[ROOT/'human/mos-tests']
manifest={'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'hardware_tested':False,'excluded':'disposable full SD images and Python bytecode; intentional test symlinks are retained as metadata only','symlinks':symlinks,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files+sources))}}
(dest/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(dest/'qualification.tar.gz','w:gz') as tar:
 for p in sorted(set(files+sources)):tar.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
archive=dest/'qualification.tar.gz';(dest/'qualification.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  qualification.tar.gz\n')
print(str(archive),archive.stat().st_size)
