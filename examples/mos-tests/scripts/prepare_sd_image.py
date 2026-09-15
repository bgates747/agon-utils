"""Create a bounded FAT32 test image, copy fixtures, and verify readback."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, tempfile, struct
ROOT = Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=ROOT/"bin/mos-tests.bin")
    parser.add_argument("--output", type=Path, default=ROOT/".emulator/test-sd.img")
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    output = args.output.resolve()
    if output.exists(): parser.error("Output already exists; choose a fresh trial image")
    output.parent.mkdir(parents=True,exist_ok=True)
    tools = ROOT/".emulator/tools/mtools/usr/bin"
    mcopy = shutil.which("mcopy") or str(tools/"mcopy")
    mmd = shutil.which("mmd") or str(tools/"mmd")
    mkfs = shutil.which("mkfs.fat") or "/usr/sbin/mkfs.fat"
    env = os.environ.copy(); env["MTOOLS_SKIP_CHECK"] = "0"
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage=Path(temporary); image=stage/"sd.img"
        with image.open("wb") as stream: stream.truncate(64*1024*1024)
        subprocess.run([mkfs,"-F","32","-h","2048","-n","MOSTESTS",str(image)],check=True)
        subprocess.run([mmd,"-i",str(image),"::/mystuff"],check=True,env=env)
        startup=stage/"boot.obey"
        startup.write_bytes(b"SET KEYBOARD 1\r\ncd /mystuff\r\nload test.bin\r\nrun\r\n")
        manifest={}
        for source,target in [(binary,"/mystuff/test.bin"),(startup,"/!boot.obey")]:
            subprocess.run([mcopy,"-i",str(image),str(source),"::"+target],check=True,env=env)
            check=stage/(source.name+".readback")
            subprocess.run([mcopy,"-i",str(image),"::"+target,str(check)],check=True,env=env)
            assert source.read_bytes()==check.read_bytes(),target
            manifest[target]=dict(sha256=digest(source),size=source.stat().st_size)
        # Wrap the verified FAT volume in an MBR partition at LBA 2048.
        disk=stage/"disk.img"
        mbr=bytearray(512)
        mbr[446:462]=struct.pack("<B3sB3sII",0,b"\xfe\xff\xff",0x0c,b"\xfe\xff\xff",2048,131072)
        mbr[510:512]=b"\x55\xaa"
        with disk.open("wb") as target:
            target.write(mbr); target.seek(1048576)
            with image.open("rb") as volume: shutil.copyfileobj(volume,target)
        # Verify the assembled disk through its partition offset too.
        for source,target in [(binary,"/mystuff/test.bin"),(startup,"/!boot.obey")]:
            check=stage/(source.name+".partition-readback")
            subprocess.run([mcopy,"-i",str(disk)+"@@1048576","::"+target,str(check)],check=True,env=env)
            assert source.read_bytes()==check.read_bytes(),target
        os.replace(disk,output)
    receipt=dict(backend="mbr-fat32-image",image=str(output),sha256=digest(output),files=manifest)
    output.with_suffix(output.suffix+".json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
if __name__=="__main__": main()
