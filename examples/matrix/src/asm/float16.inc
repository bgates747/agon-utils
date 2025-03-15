; inputs: uh.l is the signed 16.8 fixed place number to convert
; outputs: signed 16-bit IEEE‑754 (half-precision) floating point number in hl
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
