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
    ; ld hl,0x4000 ; 2.0, 16.8 fixed = 0x000200 | Biased exp: 16 (10000), True exp: 1 (00001)
    ; ld de,0x4200 ; 3.0, 16.8 fixed = 0x000300 | Biased exp: 16 (10000), True exp: 1 (00001)
    ; ; ld hl,0x4600 ; 6.0, 16.8 fixed = 0x000600 | Biased exp: 17 (10001), True exp: 2 (00010)

    ; ld hl,0x5A40 ; 200.0, 16.8 fixed = 0x00C800 | Biased exp: 22 (10110), True exp: 7 (00111)
    ; ld de,0x5CB0 ; 300.0, 16.8 fixed = 0x012C00 | Biased exp: 23 (10111), True exp: 8 (01000)
    ; ; ld hl,0x7B53 ; 60000.0, 16.8 fixed = 0xEA6000 | Biased exp: 30 (11110), True exp: 15 (01111)

    ; ld hl,0x5A40 ; 200.0, 16.8 fixed = 0x00C800 | Biased exp: 22 (10110), True exp: 7 (00111)
    ; ld de,0x34CD ; 0.3, 16.8 fixed = 0x00004D | Biased exp: 13 (01101), True exp: -2 (-0010)
    ; ; ld hl,0x5380 ; 60.0, 16.8 fixed = 0x003C00 | Biased exp: 20 (10100), True exp: 5 (00101)

    ; ld hl,0x3266 ; 0.2, 16.8 fixed = 0x000033 | Biased exp: 12 (01100), True exp: -3 (-0011)
    ; ld de,0x34CD ; 0.3, 16.8 fixed = 0x00004D | Biased exp: 13 (01101), True exp: -2 (-0010)
    ; ; ld hl,0x2BAE ; 0.06, 16.8 fixed = 0x00000F | Biased exp: 10 (01010), True exp: -5 (-0101)

    ; ld hl,0x251F ; 0.02, 16.8 fixed = 0x000005 | Biased exp: 9 (01001), True exp: -6 (-0110)
    ; ld de,0x27AE ; 0.03, 16.8 fixed = 0x000008 | Biased exp: 9 (01001), True exp: -6 (-0110)
    ; ; ld hl,0x10EA ; 0.0006, 16.8 fixed = 0x000000 | Biased exp: 4 (00100), True exp: -11 (-1011)

    ; ld hl,0x1FFF ; 0.007808684396234746, 16.8 fixed = 0x000002 | Biased exp: 7 (00111), True exp: -8 (-1000)
    ; ld de,0x1FFF ; 0.007808684396234746, 16.8 fixed = 0x000002 | Biased exp: 7 (00111), True exp: -8 (-1000)
    ; ; ld hl,0x03FF ; 6.0975552e-05, 16.8 fixed = 0x000000 | Biased exp: 0 (00000), True exp: -15 (-1111)

    ; call smul_fixed16
    ; call dumpRegistersHex

    ; call make_table
    ; call time_fixed24_to_float16
    ; call compare_fixed24_to_float16

    ret

    include "files.inc"