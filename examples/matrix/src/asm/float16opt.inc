
; inputs: uhl is the fixed place number to convert, a is the number of fractional bits
; outputs: signed 16-bit IEEE‑754 (half-precision) floating point number in hl, hlu=0
; destroys: af, de (if uhl is negative)
fixed24_to_float16:
; test uh.l for sign / zero
    add hl,de
    or a
    sbc hl,de 
    ret z ; already in proper format

    push af  ; save sign flag and fractional bits
    jr p,@F ; uh.l is positive
    
; negate uh.l
    ex de,hl
    ld hl,1 ; not 0 because carry is set if we're here
    sbc hl,de

@@: pop af ; fractional bits
    push af ; save sign flag 
    sub a,-23 ; bias the exponent
@exp_loop:
    dec a ; decrement exponent
    add hl,hl ; left shift uhl
    jr nc,@exp_loop ; loop until first non-zero mantissa bit shifts into carry

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

; zero hlu
    dec hl
    inc.s hl

    ret

; inputs: uh.l is the signed 16.8 fixed place number to convert
; outputs: signed 16-bit IEEE‑754 (half-precision) floating point number in hl
; destroys: af
; optimised by calc84maniac https://discord.com/channels/1158535358624039014/1282290921815408681/1350583315698286603
fixed24_to_float16_opt:
; test uh.l for sign / zero
    add hl,de
    xor a
    sbc hl,de 
    ret z ; already in proper format
    jp p,@F ; uh.l is positive
; negate uh.l
    add hl,de
    ex de,hl
    or 32 ; set sign bit / clear carry
    sbc hl,de

@@: or 31 ; bias the exponent
@exp_loop:
    dec a ; decrement exponent
    add hl,hl ; left shift uhl
    jr nc,@exp_loop ; loop until first non-zero mantissa bit shifts into carry

; rotate bottom 2 mantissa bits into hlu
; and top two mantissa bits into a
    add hl,hl
    adc a,a
    add hl,hl
    adc a,a
    ld h,a ; exponent and top 2 bits of mantissa to h

; a -> h, hlu -> a -> l
    dec sp
    push hl
    ld h,a ; exponent and top 2 bits of mantissa to h
    inc sp 
    pop af
    ld l,a ; bottom 8 bits of mantissa to l

; zero hlu
    dec hl
    inc.s hl

    ret
