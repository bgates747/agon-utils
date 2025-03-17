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
    include "f24/f24abs.z80"
    include "f24/f24acos.z80"
    include "f24/f24acosh.z80"
    include "f24/f24add.z80"
    include "f24/f24amean.z80"
    include "f24/f24asin.z80"
    include "f24/f24asinh.z80"
    include "f24/f24atan.z80"
    include "f24/f24atanh.z80"
    include "f24/f24bg.z80"
    include "f24/f24cmp.z80"
    include "f24/f24cos.z80"
    include "f24/f24cosh.z80"
    include "f24/f24div_pow2.z80"
    include "f24/f24div.z80"
    include "f24/f24exp.z80"
    include "f24/f24geomean.z80"
    include "f24/f24log.z80"
    include "f24/f24log2.z80"
    include "f24/f24log10.z80"
    include "f24/f24logy.z80"
    include "f24/f24mod1.z80"
    include "f24/f24mul.z80"
    include "f24/f24mul2.z80"
    include "f24/f24mul3.z80"
    include "f24/f24neg.z80"
    include "f24/f24pow.z80"
    include "f24/f24pow2.z80"
    include "f24/f24pow10_LUT.z80"
    include "f24/f24pow10.z80"
    include "f24/f24rand.z80"
    include "f24/f24sin.z80"
    include "f24/f24sinh.z80"
    include "f24/f24sqr.z80"
    include "f24/f24sqrt.z80"
    include "f24/f24sub.z80"
    include "common/mul16.z80"
    include "common/rand.z80"
    include "common/sqrt16.z80"
    
    include "debug.inc"

main:
    ld hl,0x4000 ; 2.0, 16.8 fixed = 0x000200 | Biased exp: 16 (10000), True exp: 1 (00001)
    ld de,0x4200 ; 3.0, 16.8 fixed = 0x000300 | Biased exp: 16 (10000), True exp: 1 (00001)
    ; ld hl,0x4600 ; 6.0, 16.8 fixed = 0x000600 | Biased exp: 17 (10001), True exp: 2 (00010)

    ld hl,0x5A40 ; 200.0, 16.8 fixed = 0x00C800 | Biased exp: 22 (10110), True exp: 7 (00111)
    ld de,0x5CB0 ; 300.0, 16.8 fixed = 0x012C00 | Biased exp: 23 (10111), True exp: 8 (01000)
    ; ld hl,0x7B53 ; 60000.0, 16.8 fixed = 0xEA6000 | Biased exp: 30 (11110), True exp: 15 (01111)

    ld hl,0x5A40 ; 200.0, 16.8 fixed = 0x00C800 | Biased exp: 22 (10110), True exp: 7 (00111)
    ld de,0x34CD ; 0.3, 16.8 fixed = 0x00004D | Biased exp: 13 (01101), True exp: -2 (-0010)
    ; ld hl,0x5380 ; 60.0, 16.8 fixed = 0x003C00 | Biased exp: 20 (10100), True exp: 5 (00101)

    ; ld hl,0x3266 ; 0.2, 16.8 fixed = 0x000033 | Biased exp: 12 (01100), True exp: -3 (-0011)
    ; ld de,0x34CD ; 0.3, 16.8 fixed = 0x00004D | Biased exp: 13 (01101), True exp: -2 (-0010)
    ; ; ld hl,0x2BAE ; 0.06, 16.8 fixed = 0x00000F | Biased exp: 10 (01010), True exp: -5 (-0101)

    ; ld hl,0x251F ; 0.02, 16.8 fixed = 0x000005 | Biased exp: 9 (01001), True exp: -6 (-0110)
    ; ld de,0x27AE ; 0.03, 16.8 fixed = 0x000008 | Biased exp: 9 (01001), True exp: -6 (-0110)
    ; ; ld hl,0x10EA ; 0.0006, 16.8 fixed = 0x000000 | Biased exp: 4 (00100), True exp: -11 (-1011)

    ; ld hl,0x1FFF ; 0.007808684396234746, 16.8 fixed = 0x000002 | Biased exp: 7 (00111), True exp: -8 (-1000)
    ; ld de,0x1FFF ; 0.007808684396234746, 16.8 fixed = 0x000002 | Biased exp: 7 (00111), True exp: -8 (-1000)
    ; ; ld hl,0x03FF ; 6.0975552e-05, 16.8 fixed = 0x000000 | Biased exp: 0 (00000), True exp: -15 (-1111)

    call smul_fixed16
    call dumpRegistersHex

    ; call make_table
    ; call time_fixed24_to_float16
    ; call compare_fixed24_to_float16

    ret

; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af, de
smul_fixed16:
; stack the sign bits in carry
    bit 7,h
    push af
    bit 7,d
    push af
; get hl's stored exponent
    ld a,h
    and %01111100
; stored mantissa of zero means subnormal number
; so no need to adjust mantissa or exponent
    jr z,@F 
; compute hl's true exponent
    srl a
    srl a
    sub a,15
; put the explicit 1 into the mantissa
    set 2,h
@@: push af ; stack the true exponent
; mask out everything but the top three bits of hl's mantissa
    ld a,h
    and %00000111
    ld h,a
; de gets the exact same treatment as hl
    ld a,d
    and %01111100
    jr z,@F
    srl a
    srl a
    sub a,15
    set 2,d
@@: push af 
    ld a,d
    and %00000111
    ld d,a
; multiply the mantissae
    call umul24 ; TODO: a 11x11->22 multiply would be more efficient
; compute the biased exponent
    pop af ; a = true exponent of de
    pop de ; d = true exponent of hl
    add a,d ; a = true exponent of product
    add a,19 ; a = biased exponent assuming normal product
; normalise the result
@exp_loop:
    dec a
    add hl,hl ; left shift uhl
    jr nc,@exp_loop ; loop until first non-zero mantissa bit shifts into carry
; check exponent for underflow
    cp 16
    jr nz,@skip_none
    xor a ; set stored exponent to zero
    jr @skip_one
; rotate bottom 2 mantissa bits into hlu
; and top two mantissa bits into a
@skip_none:
    add hl,hl
    adc a,a
@skip_one:
    add hl,hl
    adc a,a
    ld h,a ; exponent and top 2 bits of mantissa to h
; hlu -> a -> l
    dec sp
    push hl
    inc sp 
    pop af
    ld l,a ; bottom 8 bits of mantissa to l
; zero uhl
    dec hl
    inc.s hl
; determine sign of product
    pop af ; sign of de to carry
    jr c,@de_neg
    pop af ; sign of hl to carry
    ret nc ; both positive, nothing to do
    bit 7,h ; set sign bit to negative
    ret
@de_neg:
    pop af ; sign of hl to carry
    ret c ; both negative, nothing to do
    bit 7,h ; set sign bit to negative
    ret    
; end smul_fixed16

    include "files.inc"