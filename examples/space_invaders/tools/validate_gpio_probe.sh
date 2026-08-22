#!/bin/sh
set -eu

if [ "$#" -ne 4 ]; then
	echo "usage: $0 BINARY MAP OBJECT GPIO_DRIVER_LIBRARY" >&2
	exit 2
fi

binary=$1
map=$2
object=$3
driver=$4

fail()
{
	echo "GPIO probe validation failed: $*" >&2
	exit 1
}

hex_at()
{
	od -An -v -tx1 -j "$2" -N "$3" "$1" | tr -d ' \n'
}

test -f "$binary" || fail "missing binary: $binary"
test -f "$map" || fail "missing map: $map"
test -f "$object" || fail "missing object: $object"
test -f "$driver" || fail "missing static GPIO driver: $driver"

driver_sha=$(sha256sum "$driver" | awk '{print $1}')
test "$driver_sha" = \
	"a4234409ca9fd9479c3e2be7c717824e6196dc033ec3073149ebc72a6486a946" || \
	fail "static GPIO driver identity mismatch: $driver_sha"

size=$(wc -c < "$binary" | tr -d ' ')
test "$size" -le 65536 || fail "probe exceeds one ADL=0 bank: $size bytes"

test "$(hex_at "$binary" 0 1)" = "c3" || fail "entry is not an ADL=0 JP"
test "$(hex_at "$binary" 64 5)" = "4d4f530000" || \
	fail "MOS header is not version 0 with ADL=0 mode"

grep -Eq '0x0*40[[:space:]]+__mos_header([[:space:]]|$)' "$map" || \
	fail "map does not place __mos_header at 0x0040"
grep -Eq '0x0*45[[:space:]]+__start([[:space:]]|$)' "$map" || \
	fail "map does not place __start at 0x0045"
nm -a "$object" | grep -Eq '[[:space:]]gpio_video_driver_image$' || \
	fail "object does not contain the bundled static GPIO driver"

echo "GPIO raster probe validation: OK ($size bytes, ADL=0, static driver, mode 8)"
