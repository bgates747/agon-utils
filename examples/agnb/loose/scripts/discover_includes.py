#!/usr/bin/env python3
"""Iteratively discover missing assembly dependencies for the loose app.

This is a temporary scaffolding tool, not an implementation generator. It may
append an empty label only when ez80asm reports an unknown symbol used directly
as a CALL/JP/JR target. Constants, data references, offsets, and all other
diagnostics are reported and left for human evaluation.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = HARNESS_DIR.parents[2]
ASSEMBLY_DIR = HARNESS_DIR / "src" / "asm"
INCLUDES_FILE = ASSEMBLY_DIR / "includes.inc"
DO_ASSEMBLY = HARNESS_DIR / "scripts" / "do_assembly.py"
ROUTINE_MANIFEST = (
    HARNESS_DIR / "src" / "asm" / "routine-manifest.txt"
)

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
UNKNOWN_IDENTIFIER = re.compile(
    r'File "(?P<file>[^"]+)" line (?P<line>\d+) - Unknown identifier\s+'
    r"'(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)'"
)
CONTROL_TARGET = re.compile(
    r"^\s*(?:call(?:\.lil)?|jp(?:\.lil)?|jr)\s+"
    r"(?:(?:nz|z|nc|c|po|pe|p|m),\s*)?"
    r"(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s*(?:;.*)?$",
    re.IGNORECASE,
)
DEFINED_LABEL = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*):", re.MULTILINE)
MANIFEST_ENTRY = re.compile(
    r"^(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s+line\s+(?P<line>\d+)\b"
)


def run_assembler() -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(DO_ASSEMBLY), "-a"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    diagnostic = ANSI_ESCAPE.sub("", result.stdout + result.stderr)
    return result.returncode, diagnostic


def source_line(filename: str, line_number: int) -> tuple[Path, str]:
    source_file = Path(filename)
    if not source_file.is_absolute():
        source_file = ASSEMBLY_DIR / source_file
    lines = source_file.read_text().splitlines()
    if not 1 <= line_number <= len(lines):
        raise RuntimeError(
            f"Diagnostic line {line_number} is outside {source_file}"
        )
    return source_file, lines[line_number - 1]


def find_definition(symbol: str) -> tuple[str, int] | None:
    lines = ROUTINE_MANIFEST.read_text().splitlines()
    section = None
    for index, line in enumerate(lines):
        if (
            index + 1 < len(lines)
            and set(lines[index + 1]) == {"-"}
            and line.endswith((".asm", ".inc"))
        ):
            section = line
            continue
        match = MANIFEST_ENTRY.match(line)
        if (
            section
            and section != "includes.inc"
            and match
            and match.group("symbol") == symbol
        ):
            return section, int(match.group("line"))
    return None


def append_empty_label(symbol: str, source_file: Path, line_number: int) -> None:
    existing = INCLUDES_FILE.read_text() if INCLUDES_FILE.exists() else ""
    if symbol in DEFINED_LABEL.findall(existing):
        raise RuntimeError(f"{symbol} is already defined in {INCLUDES_FILE}")

    definition = find_definition(symbol)
    if definition:
        definition_text = f"defined in {definition[0]}:{definition[1]}; "
    else:
        definition_text = "definition not found in routine manifest; "
    separator = "" if not existing or existing.endswith("\n") else "\n"
    with INCLUDES_FILE.open("a") as output:
        output.write(
            f"{separator}{symbol}: ; {definition_text}referenced by "
            f"{source_file.name}:{line_number}\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover safe missing routine labels by assembling repeatedly."
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum assembly attempts (default: 10).",
    )
    args = parser.parse_args()
    if args.max_iterations < 1:
        parser.error("--max-iterations must be positive")

    for attempt in range(1, args.max_iterations + 1):
        returncode, diagnostic = run_assembler()
        print(f"\n=== assembly attempt {attempt}/{args.max_iterations} ===")
        print(diagnostic.rstrip())

        if returncode == 0:
            print("\nAssembly succeeded; no further placeholders are needed.")
            return 0

        match = UNKNOWN_IDENTIFIER.search(diagnostic)
        if not match:
            print(
                "\nStopped: this is not a recognized missing-identifier error; "
                "human evaluation is required.",
                file=sys.stderr,
            )
            return 1

        filename = match.group("file")
        line_number = int(match.group("line"))
        symbol = match.group("symbol")
        try:
            source_file, instruction = source_line(filename, line_number)
        except (OSError, RuntimeError) as error:
            print(f"\nStopped: {error}", file=sys.stderr)
            return 1

        control_match = CONTROL_TARGET.match(instruction)
        if not control_match or control_match.group("symbol") != symbol:
            print(
                f"\nStopped: {symbol} is used by `{instruction.strip()}`. "
                "It may be a constant, offset, or data address, so no definition "
                "was guessed.",
                file=sys.stderr,
            )
            return 1

        try:
            append_empty_label(symbol, source_file, line_number)
        except (OSError, RuntimeError) as error:
            print(f"\nStopped: {error}", file=sys.stderr)
            return 1
        print(f"\nAdded empty routine placeholder: {symbol}:")

    print(
        f"\nStopped after the requested {args.max_iterations} assembly attempts."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
