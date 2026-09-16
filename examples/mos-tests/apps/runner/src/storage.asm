; Preserve BOTH FatFS results; AgonDev ffs_fwrite returns only the byte count.
 .assume adl=1
 .include "agon/mos.inc"
 .section .text
 .global _recording_write
_recording_write:
 push ix
 ld ix,0
 add ix,sp
 ld hl,(ix+6)
 ld de,(ix+9)
 ld bc,(ix+12)
 ld a,ffs_fwrite
 rst.lil 08h
 ld de,(ix+15)
 ld (de),a
 push bc
 pop hl
 pop ix
 ret
