 .assume adl=1
 .section .text
 .global _startup_probe
 .global _startup_command_done
 .global _startup_sample
 .global _startup_kind
_startup_probe:
 push ix
 push iy
 ld bc,010203h
 ld de,040506h
 ld hl,070809h
 ld ix,00a0b0ch
 ld iy,00d0e0fh
 ld a,(_startup_sample)
 or a
 jr z,seeded
 ld bc,0fefdfch
 ld de,0fbfaf9h
 ld hl,0f8f7f6h
 ld ix,0f5f4f3h
 ld iy,0f2f1f0h
seeded:
 ld a,(_startup_kind)
 or a
 jr z,preserve
 call _capture_before
 push ix
 pop hl
 ld a,(_startup_sample)
 or a
 jr z,clobber0
 ld ix,075f4f3h
 jr captured
clobber0:
 ld ix,08a0b0ch
captured:
 ; Restore all state except the deliberately changed IX upper byte.
 ld hl,(0b7e908h)
 push hl
 ld hl,(0b7e900h)
 push hl
 pop af
 pop hl
 call _capture_after
 jr finish
preserve:
 call _capture_before
 call _capture_after
finish:
 pop iy
 pop ix
 ret
_startup_command_done:
 ret
 .section .data
_startup_sample: db 0
_startup_kind: db 0
 .include "../runner/src/capture.asm"
 .include "../runner/src/storage.asm"
