    assume adl=1 
    org 0x040000 
    jp start 
    align 64 
    db "MOS" 
    db 00h 
    db 01h 

start: 
    push af
    push bc
    push de
    push ix
    push iy

    call main
exit:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0

    ret

; API INCLUDES
    include "mos_api.inc"
    include "macros.inc"
    include "functions.inc"
    include "arith24.inc"
    include "maths.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_buffered_api.inc"
    include "vdu_plot.inc"

; APPLICATION INCLUDES
    include "softfloat/f16_mul.inc"
    include "softfloat/internals.inc"
    include "softfloat/s_normSubnormalF16Sig.inc"
    include "softfloat/s_roundPackToF16.inc"
    include "softfloat/s_shiftRightJam32.inc"
    include "debug.inc"

main:
    call vdu_cls


    ; jp test_file

    ld hl,0x8001

    call printUnpackF16

    ld c,0x80
    ld b,0xf5
    ld hl,0x4213

    call softfloat_roundPackToF16

    call printUnpackF16

    ret

; end main

; TEST FILE
; -------------------------------------------
test_file:
    ld hl,f16_fil
    ld de,mul_16_32_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    jr z,@F
    call printInline
    asciz "Error opening file for reading\r\n"
    ret
@@:
    ld hl,f16_fil_out
    ld de,mul_16_32_filename_out
    ld c,fa_write | fa_open_existing
    FFSCALL ffs_fopen
    or a
    jr z,@start
    call printInline
    asciz "Error opening file for writing\r\n"
    ret
@start:
    ld hl,0 ; error counter
    push hl ; save error counter
    ld ix,filedata
@loop:
    ld hl,f16_fil
    ld de,filedata
    ld bc,16 ; bytes per record
    FFSCALL ffs_fread
    push bc
    pop hl
    add hl,de
    or a
    sbc hl,de
    jr z,@end
    ld c,(ix+0) ; sign
    ld b,(ix+1) ; exponent
    ld l,(ix+2) ; sig low byte
    ld h,(ix+3) ; sig high byte
    call softfloat_roundPackToF16
    ld (ix+10),l ; packed_a low byte
    ld (ix+11),h ; packed_a high byte
    ld (ix+12),c ; sign_a
    ld (ix+13),b ; exponent_a
    ld (ix+14),l ; mantissa_a low byte
    ld a,h
    and %00000011
    ld h,a ; prelim mantissa high byte
    ld a,b ; exponent
    or a ; check for zero
    jr z,@F ; skip if subnormal
    set 2,h ; set implied 1 bit for normals
@@:
    ld (ix+15),h ; mantissa high byte
; write to file
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,16 ; bytes per record
    FFSCALL ffs_fwrite
; check for error
    ld l,(ix+4) ; packed_p low byte
    ld h,(ix+5) ; packed_p high byte
    ld e,(ix+10) ; packed_a low byte
    ld d,(ix+11) ; packed_a high byte
    or a ; clear carry
    sbc.s hl,de
    jr nz,@error
    jp @loop
@error:
    pop hl ; restore error counter
    inc hl
    push hl
    jp @loop
@end:
    pop hl ; restore error counter
    call printDec
    call printInline
    asciz " errors\r\n"

    ld hl,f16_fil
    FFSCALL ffs_fclose

    ld hl,f16_fil_out
    FFSCALL ffs_fclose

    ret

mul_16_32_filename: asciz "softfloat_roundPackToF16.bin"
mul_16_32_filename_out: asciz "softfloat_roundPackToF16.bin"

printUnpackF16:
    PUSH_ALL
    call printHexHL
    call printBinHL
    ld a,h
    and 0x80
    call printHexA
    ld a,h
    and %01111100
    rra
    rra
    call printHexA
    res 2,h
    or a
    jr z,@F
    set 2,h
@@:
    ld a,h
    and %00000111
    ld h,a
    call printHexHL
    call printBinHL
    call printNewLine
    POP_ALL
    ret

    include "files.inc"