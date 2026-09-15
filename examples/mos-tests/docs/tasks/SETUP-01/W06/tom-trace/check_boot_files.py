"""W06 raw-image qualification attempt; currently reproduces a pre-main MOS fault."""
from pathlib import Path
import hashlib, json, os, pty, re, select, shutil, subprocess, time
W = Path(__file__).resolve().parent.parent
FIXTURES = W.parent / "W04"
PROJECT = W.parents[3]
PROFILE = PROJECT / ".emulator"
EXPECTED = b"W04: MOS ABI 0123456789 AaZz !?\r\n"
ANSI = re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbol(text, name):
    matches = re.findall(r"^\s*0x([0-9a-f]+)\s+" + re.escape(name) + r"\s*$", text, re.M)
    assert len(matches) == 1, (name, matches)
    return int(matches[0], 16)

def observe(variant):
    project = FIXTURES / variant
    evidence = W / "tom-trace" / "boot-files-present" / variant
    evidence.mkdir(parents=True, exist_ok=True)
    with (evidence / "build.txt").open("w") as log:
        for command in (["make", "clean"], ["make", "V=", "listings"]):
            subprocess.run(command, cwd=project, stdout=log, stderr=subprocess.STDOUT, check=True)
    binary = project / "bin" / f"w04-{variant}.bin"
    mapfile = binary.with_suffix(".map")
    main = symbol(mapfile.read_text(), "_main")
    returned = symbol(mapfile.read_text(), "___exithl")
    assert binary.read_bytes()[64:69] == b"MOS\x00\x01"
    for f in (project / "bin").iterdir():
        shutil.copy2(f, evidence / f.name)
    destination = PROFILE / "tom-boot-files.img"

    autoexec = PROFILE / "sdcard/autoexec.txt"
    before = autoexec.read_bytes()
    raw = bytearray()
    proc = None
    master = None
    started = time.monotonic()
    try:
        master, slave = pty.openpty()
        env = os.environ.copy()
        env.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        proc = subprocess.Popen([str(PROJECT.parents[1]/".venv/bin/python"), str(PROJECT/"scripts/run_emulator.py"), "--image", str(destination), "-d", "-b", "0"],
            cwd=PROFILE, env=env, stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
        os.close(slave)
        def wait_prompt(offset, timeout=30):
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                cleaned = ANSI.sub(b"", bytes(raw[offset:]))
                if b">> " in cleaned:
                    return
                if select.select([master], [], [], .1)[0]:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError as error:
                        raise RuntimeError("PTY closed before expected prompt") from error
                    if not chunk:
                        raise RuntimeError("EOF before expected prompt")
                    raw.extend(chunk)
                if proc.poll() is not None:
                    raise RuntimeError("Emulator exited before checkpoint")
            raise TimeoutError("No debugger prompt within 30 seconds; run is incomplete")
        def command(text):
            offset = len(raw)
            os.write(master, (text + "\n").encode())
            wait_prompt(offset)
        wait_prompt(0)
        command(f"trigger ${main:x} state")
        command("trigger $10 state")
        command(f"trigger ${returned:x} pause : state")
        command("delete $0")
        command("c")
        # Return trigger has paused before crt0 exit processing.
        os.write(master, b"exit\n")
        proc.wait(timeout=5)
        assert proc.returncode == 0, proc.returncode
        text = ANSI.sub(b"", bytes(raw)).decode(errors="replace")
        states = re.findall(r"\* ([0-9a-f]{6}):([^\r\n]*)", text)
        entry = [s for pc, s in states if int(pc, 16) == main]
        final = [s for pc, s in states if int(pc, 16) == returned]
        assert len(entry) == len(final) == 1, "Missing or repeated entry/return"
        output = bytes(int(re.search(r"AF:([0-9a-f]{2})", s)[1],16)
            for pc, s in states if int(pc,16) == 0x10)
        assert output == EXPECTED, repr(output)
        def reg(s, name): return int(re.search(name + r":([0-9a-f]+)", s)[1], 16)
        assert reg(final[0], "HL") == 0x123456, final
        assert reg(final[0], "SPL") == reg(entry[0], "SPL") + 3, "Stack not balanced across main RET"
        assert reg(final[0], "IX") == reg(entry[0], "IX"), "IX not preserved"
        assert "out of bounds" not in text.lower()
        result = dict(variant=variant, passed=True, backend="mbr-fat32-image", binary_sha256=sha(binary),
            main_address=hex(main), return_address=hex(returned), output_hex=output.hex(),
            return_hl="123456", stack_balanced=True, ix_preserved=True,
            elapsed_seconds=round(time.monotonic()-started,3), emulator_exit=proc.returncode)
        (evidence / "captured-output.bin").write_bytes(output)
        (evidence / "result.json").write_text(json.dumps(result, indent=2)+"\n")
        return result
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
        if master is not None: os.close(master)
        (evidence / "debugger.raw.txt").write_bytes(raw)
        (evidence / "debugger.txt").write_bytes(ANSI.sub(b"", bytes(raw)))
        autoexec.write_bytes(before)
        if destination.exists():
            (evidence/"image-after.sha256").write_text(sha(destination)+"\n")
        # Preserve raw image in ignored profile for this trial.

if __name__ == "__main__":
    results = [observe("cpp")]

    print(json.dumps(results, indent=2))
