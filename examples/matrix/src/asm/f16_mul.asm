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

    MACRO PRINT_HL_HEX_BIN msg
        push de
        push af
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        push hl
        call printHLHexBin
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO DUMP_REGISTERS_HEX msg
        push de
        push af
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        pop af
        pop de
        call dumpRegistersHex
        ; call dumpFlags
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
    jp test_file

; --- Inputs / Outputs ---
; 3830 00111000 00110000 00 0e 0430 100 00110000 0.5234375 sigA
; f828 11111000 00101000 80 1e 0428 100 00101000 -34048.0 sigB
; f45a 11110100 01011010 80 1d 045a 100 01011010 -17824.0 Expected Result
; fc00 11111100 00000000 80 1f 0400 100 00000000 -inf Assembly Result

; --- Intermediate Results ---
; 4300 01000011 00000000  sigA (<<4, normalized)
; 8500 10000101 00000000  sigB (<<5, normalized)
; 22cf 00100010 11001111  sig32Z >> 16 (upper 16 bits of 32-bit product)
; 0000 00000000 00000000  sig32Z & 0xFFFF (lower 16 bits of 32-bit product)
; expA = -1, expB = 15, expA + expB = 14

; --- Generated Assembly Test Code ---
    ld hl,0x3830
    ld de,0xF828
    ld bc,0xF45A

    jp test_manual

; passes
    ld hl,0x7c00 ; +infinity
    ld de,0xfc00 ; -infinity
    ld bc,0xfc00 ; -infinity
    call test_multiple

; passes
    ld hl,0xfc00 ; -infinity
    ld de,0x7c00 ; +infinity
    ld bc,0xfc00 ; -infinity
    call test_multiple

; passes
    ld hl,0x7c00 ; +infinity
    ld de,0x7c00 ; +infinity
    ld bc,0x7c00 ; +infinity
    call test_multiple

; passes
    ld hl,0xfc00 ; -infinity
    ld de,0xfc00 ; -infinity
    ld bc,0x7c00 ; +infinity
    call test_multiple

; passes
    ld hl,0x0000 ; +zero
    ld de,0x7c00 ; +infinity
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x7c00 ; +infinity
    ld de,0x0000 ; +zero
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x0000 ; +zero
    ld de,0x0000 ; +zero
    ld bc,0x0000 ; +zero
    call test_multiple

; passes
    ld hl,0x0000 ; +0
    ld de,0x8000 ; -0
    ld bc,0x8000 ; expected: -0
    call test_multiple

; passes
    ld hl,0x8000 ; -0
    ld de,0x0000 ; +0
    ld bc,0x8000 ; expected: -0
    call test_multiple

; passes
    ld hl,0x8000 ; -0
    ld de,0x8000 ; -0
    ld bc,0x0000 ; +zero
    call test_multiple

; passes
    ld hl,0x7E01 ; NaN
    ld de,0x3555 ; normal
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x7E01 ; NaN
    ld de,0x3555 ; normal
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x7E01 ; NaN
    ld de,0x0000 ; +zero
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x7E01 ; NaN
    ld de,0x7C00 ; +Inf
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x3555 ; normal
    ld de,0x7E01 ; NaN
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x0001 ; subnormal
    ld de,0x7E01 ; NaN
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x0000 ; +zero
    ld de,0x7E01 ; NaN
    ld bc,0x7E00 ; NaN
    call test_multiple

; passes
    ld hl,0x7C00 ; +Inf
    ld de,0x7E01 ; NaN
    ld bc,0x7E00 ; NaN
    call test_multiple

    ld hl,0x8000
    ld de,0xEF25
    ld bc,0x0000
    call test_multiple


    ret


test_multiple:
    push bc
    call printHexHL
    ex de,hl
    call printHexHL
    ex de,hl
    call f16_mul
    call printHexHL
    ex de,hl
    pop hl ; was bc
    call printHexHL
    or a ; clear carry
    sbc hl,de
    call printHexHL
    call printNewLine
    ret


test_manual:
    push bc
    push hl
    push de
    PRINT_UNPACK_F16 "OP1:"
    pop de
    pop hl
    ex de,hl
    push hl
    push de
    PRINT_UNPACK_F16 "OP2:"
    pop hl
    pop de
    call f16_mul
    PRINT_UNPACK_F16 "Result:"
    pop hl ; was bcs
    PRINT_UNPACK_F16 "Should be:"
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
    ld bc,8 ; bytes per record
    FFSCALL ffs_fread
    push bc
    pop hl
    SIGN_HLU
    jr z,@end
    ld hl,(ix+0) ; op1
    ld de,(ix+2) ; op2
    call f16_mul
    ld (ix+6),l ; assembly product low byte
    ld (ix+7),h ; assembly product high byte
; write to file
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,8 ; bytes per record
    FFSCALL ffs_fwrite
; check for error
    ld l,(ix+6) ; assembly product low byte
    ld h,(ix+7) ; assembly product high byte
    ld e,(ix+4) ; python product low byte
    ld d,(ix+5) ; python product high byte
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

mul_16_32_filename: asciz "fp16_mul_test.bin"
mul_16_32_filename_out: asciz "fp16_mul_test.bin"

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

printHLHexBin:
    call printHexHL
    call printBinHL
    call printNewLine
    ret

    include "files.inc"