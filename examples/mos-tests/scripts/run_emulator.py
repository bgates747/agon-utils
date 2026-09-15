"""Headless raw-image entry point delegating to the canonical profile wrapper."""
from pathlib import Path
import argparse, os
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--image",type=Path,default=ROOT/".emulator/test-sd.img")
    args,extra=parser.parse_known_args()
    image=args.image.resolve(strict=True)
    if not image.is_file(): parser.error("SD image must be a regular file")
    if any(x.split("=")[0] in ("--sdcard","--sdcard-img") for x in extra):
        parser.error("Select the backend only through --image")
    profile=ROOT/".emulator"
    os.environ["SDL_VIDEODRIVER"]="dummy"
    os.environ["SDL_AUDIODRIVER"]="dummy"
    os.chdir(profile)
    os.execv(str(profile/"fab-agon-emulator"),["./fab-agon-emulator","--renderer","sw","--sdcard-img",str(image),*extra])
if __name__=="__main__": main()
