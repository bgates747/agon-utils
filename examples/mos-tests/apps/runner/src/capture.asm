.assume adl=1
.section .text
.global _capture_before
_capture_before:
 ld (0b7e908h), hl
 push af
 pop hl
 ld (0b7e900h), hl
 ld (0b7e902h), bc
 ld (0b7e905h), de
 ld (0b7e90bh), ix
 ld (0b7e90eh), iy
 ld (0b7e911h), sp
 ld hl, (0b7e911h)
 inc hl
 inc hl
 inc hl
 ld (0b7e911h), hl
 ld hl, _capture_before
 ld (0b7e914h), hl
 ld a, mb
 ld (0b7e917h), a
 ld a, 1
 ld (0b7e918h), a
 xor a
 ld (0b7e919h), a
 ld (0b7e91ch), a
 ld (0b7e91dh), a
 ld (0b7e91eh), a
 ld (0b7e91fh), a
 ld hl, 03ffh
 ld (0b7e91ah), hl
 ld hl, (0b7e900h)
 push hl
 pop af
 ld hl, (0b7e908h)
 ret
.global _capture_after
_capture_after:
 ld (0b7e928h), hl
 push af
 pop hl
 ld (0b7e920h), hl
 ld (0b7e922h), bc
 ld (0b7e925h), de
 ld (0b7e92bh), ix
 ld (0b7e92eh), iy
 ld (0b7e931h), sp
 ld hl, (0b7e931h)
 inc hl
 inc hl
 inc hl
 ld (0b7e931h), hl
 ld hl, _capture_after
 ld (0b7e934h), hl
 ld a, mb
 ld (0b7e937h), a
 ld a, 1
 ld (0b7e938h), a
 xor a
 ld (0b7e939h), a
 ld (0b7e93ch), a
 ld (0b7e93dh), a
 ld (0b7e93eh), a
 ld (0b7e93fh), a
 ld hl, 03ffh
 ld (0b7e93ah), hl
 ld hl, (0b7e920h)
 push hl
 pop af
 ld hl, (0b7e928h)
 ret

; Call before touching the fixed capture window. C int return is HL.
.global _capture_available
_capture_available:
 in0 a, (0b5h)
 cp 0b7h
 jr nz, capture_unavailable
 in0 a, (0b4h)
 and 080h
 jr z, capture_unavailable
 ld hl, 1
 ret
capture_unavailable:
 ld hl, 0
 ret
