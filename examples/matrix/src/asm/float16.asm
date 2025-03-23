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

    ld hl,0x004524 ; 5.1406250000000000e+00
    ld de,0x006080 ; 5.7600000000000000e+02
    call float16_smul_dev
    push hl
    call printInline
    asciz "\r\n2.9600000000000000e+03\r\n0069C8 00000000 01101001 11001000\r\n"

    pop hl
    call printHexUHL
    call printBinUHL
    call printNewLine

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