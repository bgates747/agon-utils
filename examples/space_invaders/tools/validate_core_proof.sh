#!/bin/sh
set -eu

if [ "$#" -ne 5 ]; then
	echo "usage: $0 BINARY MAP OBJECT REFERENCE_ROM LISTING" >&2
	exit 2
fi

binary=$1
map=$2
object=$3
reference_rom=$4
listing=$5

fail()
{
	echo "core-proof validation failed: $*" >&2
	exit 1
}

hex_at()
{
	od -An -v -tx1 -j "$2" -N "$3" "$1" | tr -d ' \n'
}

test -f "$binary" || fail "missing binary: $binary"
test -f "$map" || fail "missing map: $map"
test -f "$object" || fail "missing object: $object"
test -f "$reference_rom" || fail "missing reference ROM: $reference_rom"
test -f "$listing" || fail "missing agondev listing: $listing"

reference_size=$(wc -c < "$reference_rom" | tr -d ' ')
test "$reference_size" -eq 8192 || fail "reference ROM is not 8192 bytes"
printf '%s  %s\n' \
	7446e0994117596de5206519e693f8875ff3455e0be121d5cb975c3bcc224c4e \
	"$reference_rom" | sha256sum -c - >/dev/null

test "$(hex_at "$binary" 0 4)" = "c3008000" || \
	fail "entry jump/header prefix changed"
test "$(hex_at "$binary" 64 5)" = "4d4f530000" || \
	fail "MOS header is not version 0 ADL=0"
test "$(hex_at "$binary" 32768 4)" = "f331feff" || \
	fail "loader does not disable interrupts before replacing low memory"

# GNU cmp permits independent skips for each input. The embedded bytes must be
# identical to the independently assembled 8080 reference image.
cmp -s -n 8192 -i 20480:0 "$binary" "$reference_rom" || \
	fail "embedded original ROM differs from reference"

grep -Eq '0x0*4000[[:space:]]+__core_test_start([[:space:]]|$)' "$map" || \
	fail "test trampoline is not linked at logical 0x4000"
grep -Eq '0x0*5000[[:space:]]+__original_rom([[:space:]]|$)' "$map" || \
	fail "reference ROM is not embedded at file offset 0x5000"
grep -Eq '0x0*8000[[:space:]]+__start([[:space:]]|$)' "$map" || \
	fail "proof loader is not isolated above logical 0x8000"

# A short CALL pushes two bytes. RET.LIS pops three and previously allowed the
# tests to reach PASS before corrupting SPS and panicking the emulator.
if grep -Eq '[[:space:]]ret[.]lis([[:space:]]|$)' "$listing"; then
	fail "all-short harness contains RET.LIS"
fi

echo "core-proof validation: OK (byte-identical 8 KiB ROM, all-short ADL=0 harness)"
