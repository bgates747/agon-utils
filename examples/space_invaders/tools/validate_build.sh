#!/bin/sh
set -eu

if [ "$#" -ne 3 ]; then
	echo "usage: $0 BINARY MAP OBJECT" >&2
	exit 2
fi

binary=$1
map=$2
object=$3

fail()
{
	echo "build validation failed: $*" >&2
	exit 1
}

hex_at()
{
	od -An -v -tx1 -j "$2" -N "$3" "$1" | tr -d ' \n'
}

test -f "$binary" || fail "missing binary: $binary"
test -f "$map" || fail "missing map: $map"
test -f "$object" || fail "missing object: $object"

size=$(wc -c < "$binary" | tr -d ' ')
test "$size" -eq 77 || fail "expected 77-byte setup probe, got $size"

test "$(hex_at "$binary" 0 4)" = "c3450000" || \
	fail "entry jump is not ADL=0 JP 0x0045 followed by offset-3 padding"
test "$(hex_at "$binary" 64 5)" = "4d4f530000" || \
	fail "MOS header is not version 0 with ADL=0 mode"
test "$(hex_at "$binary" 69 8)" = "31feff21000049c9" || \
	fail "probe body does not initialize SPS, return zero, and RET.LIS"

program_name=$(od -An -v -tc -j 4 -N 13 "$binary" | tr -d ' \n')
test "$program_name" = "invaders.bin\0" || \
	fail "embedded executable name is not invaders.bin"

grep -Eq '0x0*40[[:space:]]+__mos_header([[:space:]]|$)' "$map" || \
	fail "map does not place __mos_header at 0x0040"
grep -Eq '0x0*45[[:space:]]+__start([[:space:]]|$)' "$map" || \
	fail "map does not place __start at 0x0045"

echo "build validation: OK ($size bytes, ADL=0 entry 0x0045)"
