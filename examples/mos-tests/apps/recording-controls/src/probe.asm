 .assume adl=1
 .section .text
 .global _recording_probe
 .global _recording_done
_recording_probe:
 push ix
 push iy
 ld bc,010203h
 ld de,040506h
 ld hl,070809h
 ld ix,00a0b0ch
 ld iy,00d0e0fh
 call _capture_before
 call _capture_after
 pop iy
 pop ix
 ret
_recording_done:
 ret
 .include "../runner/src/capture.asm"
 .include "../runner/src/storage.asm"
