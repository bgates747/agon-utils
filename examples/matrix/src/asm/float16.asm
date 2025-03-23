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
    include "fixed168.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_buffered_api.inc"
    include "vdu_fonts.inc"
    include "vdu_plot.inc"
    include "vdu_sound.inc"

    include "fpp.inc"
    include "fpp_ext.inc"
    include "float16.inc"
    include "timer_prt_stopwatch.inc"

; APPLICATION INCLUDES
    
    include "debug.inc"

main:
    jp test_file

    ld hl,0x00C0B9 ; -2.3613281250000000e+00
    ld de,0x00C3E5 ; -3.9472656250000000e+00
    call float16_smul_dev
    push hl
    call printInline
    asciz "\r\n9.3203125000000000e+00\r\n0048A9 00000000 01001000 10101001\r\n"

    pop hl
    call printHexUHL
    call printBinUHL
    call printNewLine

    ret

; normal product looks like this:
;      hlu       h       l
; C 76543210 76543210 76543210
; I 98765432 10GRSxxx xxxxxxxx
;   10100000 00111000 00100000

;      hlu       h       l
; C 76543210 76543210 76543210
; x 76543210 GRSxxxxx xxxxxI98  

    ld hl,%101000000011100000000000

    ld a,1
    scf

    call printCarry
    call printBinUHL
    call printNewLine

    ld b,2
@loop:
    add hl,hl
    call printCarry
    adc a,a
    ld l,a
    call printBinUHL
    call printNewLine

    djnz @loop

    call printNewLine

    call printInline
    asciz "0 10000000 11100000 00000110"
    call printNewLine

; 1 101000000011100000000001
; 1 010000000111000000000011
; 0 100000001110000000000110

    ret

    ld hl,0x00C0B9
    ld de,0x00C3E5

    call dumpFlags
    call dumpRegistersHex

    call float16_smul

    call dumpFlags
    call dumpRegistersHex
    call printNewLine

    call printHexUHL
    call printBinUHL
    call printNewLine 
    ret

    call test_file
    ret

; TEST FILE
; -------------------------------------------
test_file:
    ld hl,f16_fil
    ld de,f16_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    jr z,@F
    call printInline
    asciz "Error opening file for reading\r\n"
    ret
@@:
    ld hl,f16_fil_out
    ld de,f16_filename_out
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
    ld bc,9 ; 9 bytes for a single record
    FFSCALL ffs_fread
    push bc
    pop hl
    add hl,de
    or a
    sbc hl,de
    jr z,@end
    ld hl,(ix+0)
    ld de,(ix+3)
    call float16_smul_dev
    ld (ix+9),hl

; check for error
    ld de,(ix+6)
    or a
    sbc hl,de

; write to file
    push hl
    push af
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,13
    FFSCALL ffs_fwrite
    pop af
    pop hl
    jr z,@loop

; ignore rounding erorrs
    ; ld a,l
    ; cp -1
    ; jr z,@loop

; don't ignore rounding errors
    jr z,@loop

; ; write to file
;     ld hl,f16_fil_out
;     ld de,filedata
;     ld bc,12
;     FFSCALL ffs_fwrite

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

f16_filename: asciz "fp16_mul_test.bin"
f16_filename_out: asciz "fp16_mul_test_out.bin"

    include "files.inc"