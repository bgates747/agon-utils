"""Deploy pinned W05 interpreter/fixture into a fresh image; never modify upstream."""
from pathlib import Path
import argparse,subprocess,hashlib,json
W=Path(__file__).resolve().parent;P=W.parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--image',type=Path,default=P/'.emulator/w05-basic.img');args=parser.parse_args()
image=args.image.resolve();binary=W/'bbc-basic-v-adl.bin'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='ed6ff5a4707f941ff7b178111771a0bfade3ecdefccbb3bcb4015b9a6d5a87ab'
subprocess.run([str(P.parents[1]/'.venv/bin/python'),str(P/'scripts/prepare_sd_image.py'),'--binary',str(binary),'--output',str(image)],check=True)
mt=P/'.emulator/tools/mtools/usr/bin';spec=str(image)+'@@1048576';files={}
for source,target in [(binary,'/mystuff/bbc-basic-v-adl.bin'),(W/'fixtures/smoke.bas','/mystuff/smoke.bas'),(W/'fixtures/boot.obey','/!boot.obey')]:
 subprocess.run([str(mt/'mcopy'),'-o','-i',spec,str(source),'::'+target],check=True)
 check=subprocess.run([str(mt/'mcopy'),'-i',spec,'::'+target,'-'],capture_output=True,check=True).stdout
 assert check==source.read_bytes(),target
 files[target]=hashlib.sha256(check).hexdigest()
subprocess.run([str(mt/'mdel'),'-i',spec,'::/mystuff/test.bin'],check=True)
receipt=dict(backend='mbr-fat32-image',image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),files=files)
image.with_suffix('.img.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
