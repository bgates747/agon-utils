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

; APPLICATION INCLUDES
    
    include "debug.inc"

main:
; ; DEBUG
;     XOR A
;     LD HL,0XF00000
;     LD B,26
; @LOOP:
;     CALL dumpRegistersHex
;     ADC HL,HL
;     DJNZ @LOOP
;     RET
; ; END DEBUG


    ; ld hl,15*256 ; 15.0 -> 0x4B80
    ; ld hl,0x000180 ; 1.5 -> 0x3e00
    ; ld hl,0xFFFE80 ; -1.5 -> 0xbe00
    ; ld hl,0x7FFFFF ; 32767.99609375 -> 0x7800
    ; ld hl,0x800000 ; 32768.0 (unsigned) -> 0x7800
    ; ld hl,0x7FFF00 ; 32767.0 (signed) -> 0x7800
    ; ld hl,0x0000FF ; 0.99609375 -> 0x3F00
    ; ld hl,0xFFFFFF ; 65535.99609375 -> 0x7C00 (unsigned)
    ; ld hl,0x016698 ; 358.59375 -> 0x5D9A
    ld hl,0xFE9968 ; -358.59375 -> 0x7BF5

    ; ld hl,0

    call fixed_s168_to_float16
    call dumpRegistersHex 

    ret

; inputs: uh.l is the signed 16.8 fixed place number to convert
; outputs: 16-bit IEEE‑754 floating point number in hl
; destroys: af, de (if uh.l is negative)
fixed_s168_to_float16:
; test uh.l for sign / zero
    add hl,de
    or a
    sbc hl,de 
    ret z ; already in proper format

    push af  ; save sign flag
    jr p,@F ; uh.l is positive
    
; negate uh.l
    ex de,hl
    ld hl,1 ; not 0 because carry is set if we're here
    sbc hl,de

@@: xor a ; clear flags and zero exponent counter
@exp_loop:
    dec a ; bump exponent counter
    add hl,hl ; left shift uhl
    jr nc,@exp_loop ; loop until first non-zero mantissa bit shifts into carry
    add a,31 ; bias the exponent

; rotate bottom 2 mantissa bits into hlu
; and top two mantissa bits into a
    add hl,hl
    adc a,a
    add hl,hl
    adc a,a
    ld h,a ; exponent and top 2 bits of mantissa to h

; hlu -> a -> l
    dec sp
    push hl
    inc sp 
    pop af
    ld l,a ; bottom 8 bits of mantissa to l

; handle sign
    pop af ; restore sign flag
    ret p ; already positive
    set 7,h ; set sign negative

    ret

    include "files.inc"