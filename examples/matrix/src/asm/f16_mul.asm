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

    MACRO PRINT_UNPACK_F16 msg
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        call printUnpackF16
    ENDMACRO

    MACRO PRINT_PACK_F16 msg
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        call printPackF16
    ENDMACRO

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

    ld hl,0x4001
    ; if ( sigZ < 0x4000 ) {
    ;     --expZ;
    ;     sigZ <<= 1;
    ; }
    ex de,hl ; keep hl safe for the compare
    ld hl,0x4000
    or a ; clear carry
    sbc hl,de ; sigZ - 0x4000
    ex de,hl ; restore hl

    call dumpFlags
    ret

    ld hl,0x03ff
    call softfloat_normSubnormalF16Sig
    call printBinUHL
    call printDecS8
    call printNewLine
    ret

    jp test_file

    ld hl,0x9a42
    ld de,0x77b8
    call mul_16_32
    call printHexHLDE
    call printNewLine

    ret

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
    ld c,fa_write | fa_create_always
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
    ld bc,8 ; 8 bytes for a single record
    FFSCALL ffs_fread
    push bc
    pop hl
    add hl,de
    or a
    sbc hl,de
    jr z,@end
    ld hl,(ix+0)
    ld de,(ix+2)
    call mul_16_32
    ld (ix+8),e
    ld (ix+9),d
    ld (ix+10),l
    ld (ix+11),h
; write to file
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,12
    FFSCALL ffs_fwrite
; check for error
    ld l,(ix+4)
    ld h,(ix+5)
    ld e,(ix+8)
    ld d,(ix+9)
    sbc.s hl,de
    jr nz,@error
    ld l,(ix+6)
    ld h,(ix+7)
    ld e,(ix+10)
    ld d,(ix+11)
    or a
    sbc.s hl,de
    jr nz,@error
    jr @loop
@error:
    pop hl ; restore error counter
    inc hl
    push hl
    jr @loop
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

mul_16_32_filename: asciz "mul_16_32_test.bin"
mul_16_32_filename_out: asciz "mul_16_32_test_out.bin"

printUnpackF16:
    push af
    push bc
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
    pop bc
    pop af
    ret
; end printUnpackF16

printPackF16:
    push af
    push bc
    push hl
    ld a,b ; exponent
    or a,h
    ld h,a
    ld a,c ; sign
    or a
    ld h,a
    call printHexHL
    call printBinHL
    ld a,c ; sign
    call printHexA
    ld a,b ; exponent
    call printHexA
    pop hl ; restore sig
    call printHexHL
    call printBinHL
    call printNewLine
    pop bc
    pop af
    ret
; end printPackF16

    include "files.inc"