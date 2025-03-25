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
    call vdu_cls

    ; jp test_file

    ld hl,0x00005E ; 5.6028366088867188e-06
    ld de,0x00416D ; 2.7128906250000000e+00
    call float16_smul_dev
    call printNewLine
    call printHexUHL
    call printBinUHL
    call printInline
    asciz "\r\n0000FF 00000000 00000000 11111111\r\n"
    call printInline
    asciz "=================================\r\n\r\n"

    ld hl,0x0003EF ; 6.0021877288818359e-05
    ld de,0x003D24 ; 1.2851562500000000e+00
    call float16_smul_dev
    call printNewLine
    call printHexUHL
    call printBinUHL
    call printInline
    asciz "\r\n00050E 00000000 00000101 00001110\r\n"
    call printInline
    asciz "=================================\r\n\r\n"

    ld hl,0x000002 ; 1.1920928955078125e-07
    ld de,0x003C53 ; 1.0810546875000000e+00
    call float16_smul_dev
    call printNewLine
    call printHexUHL
    call printBinUHL
    call printInline
    asciz "\r\n000002 00000000 00000000 00000010\r\n"
    call printInline
    asciz "=================================\r\n\r\n"

    ld hl,0x00489D ; 9.2265625000000000e+00
    ld de,0x005739 ; 1.1556250000000000e+02
    call float16_smul_dev
    call printNewLine
    call printHexUHL
    call printBinUHL
    call printInline
    asciz "\r\n00642A 00000000 01100100 00101010\r\n"
    call printInline
    asciz "=================================\r\n\r\n"

    ld hl,0x00021A ; 3.2067298889160156e-05
    ld de,0x003E3F ; 1.5615234375000000e+00
    call float16_smul_dev
    call printNewLine
    call printHexUHL
    call printBinUHL
    call printInline
    asciz "\r\n000348 00000000 00000011 01001000\r\n"



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