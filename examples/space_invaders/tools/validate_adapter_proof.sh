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
	echo "adapter-proof validation failed: $*" >&2
	exit 1
}

hex_at()
{
	od -An -v -tx1 -j "$2" -N "$3" "$1" | tr -d ' \n'
}

for file in "$binary" "$map" "$object" "$reference_rom" "$listing"; do
	test -f "$file" || fail "missing input: $file"
done

test "$(wc -c < "$reference_rom" | tr -d ' ')" -eq 8192 || \
	fail "reference ROM is not 8192 bytes"
printf '%s  %s\n' \
	7446e0994117596de5206519e693f8875ff3455e0be121d5cb975c3bcc224c4e \
	"$reference_rom" | sha256sum -c - >/dev/null

test "$(hex_at "$binary" 0 4)" = "c3008000" || \
	fail "entry jump/header prefix changed"
test "$(hex_at "$binary" 64 5)" = "4d4f530000" || \
	fail "MOS header is not version 0 ADL=0"
cmp -s -n 8192 -i 20480:0 "$binary" "$reference_rom" || \
	fail "embedded original ROM differs from reference"

grep -Eq '0x0*4000[[:space:]]+__io_trap([[:space:]]|$)' "$map" || \
	fail "I/O trap is not linked at logical 0x4000"
grep -Eq '0x0*5000[[:space:]]+__original_rom([[:space:]]|$)' "$map" || \
	fail "reference ROM is not embedded at file offset 0x5000"
grep -Eq '0x0*8000[[:space:]]+__start([[:space:]]|$)' "$map" || \
	fail "proof loader is not isolated above logical 0x8000"

# The reference-side opcode/operand pairs below are the complete executable
# hardware inventory, including instructions preserved as raw DB blocks.
check_pair()
{
	offset=$((0x$1))
	expected=$2
	test "$(hex_at "$reference_rom" "$offset" 2)" = "$expected" || \
		fail "reference I/O pair changed at 0x$1"
}

for address in 0020 0791 085f 08d1 093f 0bb7 140a 1413 145a 1464 149d 14b1 15dc 15e4 17c7 17ca 17cd 19a1 19ac; do
	case "$address" in
		08d1|093f|0bb7|17ca|17cd) port=02 ;;
		140a|1413|145a|1464|149d|14b1|15dc|15e4) port=03 ;;
		*) port=01 ;;
	esac
	check_pair "$address" "db$port"
done

for pair in 031d:05 06f4:05 084c:06 090e:06 0a85:06 0aeb:03 0aed:05 0b77:06 1408:04 1411:04 1458:04 1462:04 1477:02 149b:04 14af:04 15da:04 15e2:04 16de:05 1757:05 1772:05 17bc:05 1901:03 19e3:03; do
	address=${pair%:*}
	port=${pair#*:}
	check_pair "$address" "d3$port"
done

grep -Eq '0000002a[[:space:]]+IO_PATCH_COUNT([[:space:]]|$)' "$listing" || \
	fail "expected 42 typed I/O patches"
grep -Eq '00000005[[:space:]]+EI_PATCH_COUNT([[:space:]]|$)' "$listing" || \
	fail "expected five EI patches"

echo "adapter-proof validation: OK (42 address-preserving I/O traps, five EI patches)"
