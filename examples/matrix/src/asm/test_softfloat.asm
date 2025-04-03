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
    include "softfloat/internals.inc"
    include "softfloat/s_normSubnormalF16Sig.inc"
    include "softfloat/s_roundPackToF16.inc"
    include "softfloat/s_shiftRightJam32.inc"
    include "debug.inc"

main:
    call vdu_cls

    ld hl,0x3c00 ; 1.0
    ld d,%11110000 ; rounding bits

    ; call dumpRegistersHex
    call printHexHL
    call printBinHL
    call printNewLine

    call softfloat16_unpack

    ; ; call dumpRegistersHex
    ; call printHexHL
    ; call printBinHL
    ; call printNewLine

; shift rounding bits into significand
; once
    sla d 
    adc hl,hl
; twice
    sla d
    adc hl,hl
; thrice
    sla d
    adc hl,hl
; four times
    sla d
    adc hl,hl

    ; call printHexHL
    ; call printBinHL
    ; call printNewLine

    call softfloat_roundPackToF16

    call printHexHL
    call printBinHL
    call printNewLine

    ret
; end main

mul_16_32_filename: asciz "mul_16_32_test.bin"
mul_16_32_filename_out: asciz "mul_16_32_test_out.bin"

    include "files.inc"