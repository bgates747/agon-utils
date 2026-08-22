#!/bin/sh
set -eu

if [ "$#" -ne 3 ]; then
	echo "usage: $0 TRANSLATED_BINARY REFERENCE_ROM LISTING" >&2
	exit 2
fi

translated=$1
reference=$2
listing=$3

fail()
{
	echo "translation-proof validation failed: $*" >&2
	exit 1
}

for file in "$translated" "$reference" "$listing"; do
	test -f "$file" || fail "missing input: $file"
done

printf '%s  %s\n' \
	7446e0994117596de5206519e693f8875ff3455e0be121d5cb975c3bcc224c4e \
	"$reference" | sha256sum -c - >/dev/null

compare_range()
{
	name=$1
	offset=$((0x$2))
	length=$((0x$3))
	cmp -s -n "$length" -i "$offset:$offset" "$translated" "$reference" || \
		fail "$name differs from reference at 0x$2 for 0x$3 bytes"
}

compare_range InitRack        00b1 26
compare_range InitAliens      01c0 0d
compare_range AddDelta        01d9 0b
compare_range Cnt16s          1554 0e
compare_range GetAlienStatPtr 1581 0f
compare_range BlockCopy       1a32 09
compare_range ConvToScr       1a47 15

for symbol in translated_InitRack translated_InitAliens translated_AddDelta \
	translated_Cnt16s translated_GetAlienStatPtr translated_BlockCopy \
	translated_ConvToScr; do
	grep -Eq "[[:space:]]$symbol([[:space:]]|$)" "$listing" || \
		fail "listing lacks $symbol"
done

echo "translation-proof validation: OK (seven routines, 121 exact opcode bytes)"
