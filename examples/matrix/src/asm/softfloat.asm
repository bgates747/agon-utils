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
    include "softfloat.inc"
    include "timer_prt_stopwatch.inc"

; APPLICATION INCLUDES
    
    include "debug.inc"

main:
    call vdu_cls

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

    include "files.inc"