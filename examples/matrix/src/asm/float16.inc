; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af, de
float16_smul_dev:
; determine sign of result and stack it
    ld a,h
    and %10000000
    xor d
    and %10000000
    push af ; stack the sign
; unpack hl
    push de ; TODO: figure out why DE gets stomped here
    call float16_unpack
    ; add hl,hl ; shift only first operand up one bit for some magic reason
; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     call printNewLine
; ; END DEBUG
    pop de ; restore de TODO: figure out why DE gets stomped above
    ; jr c,@hl_zero
    jp c,@hl_zero
    push af ; stack the true exponent
; unpack de
    ex de,hl
    push de ; TODO: figure out why DE gets stomped here
    call float16_unpack
; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     call printNewLine
; ; END DEBUG
    pop de ; restore de TODO: figure out why DE gets stomped above
    ex de,hl
    ; jr c,@de_zero
    jp c,@de_zero
    push af ; stack the true exponent
; multiply the mantissae
    call umul24 ; TODO: a 11x11->22 multiply would be more efficient

; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     call printNewLine
; ; END DEBUG

; determine whether we need the sticky bit
    ld a,l
    and a
    jr nz,@F ; non-zero, so need sticky
    ld a,h
    and %00000111
@@:
    ld c,a ; we test c for non-zero later to determine whether to set sticky bit

; compute product's provisional biased exponent prior to normalisation and rounding
    ld a,15+4 ; add the exponent bias
    pop de ; d = true exponent of de
    add a,d
    pop de ; d = true exponent of hl
    add a,d
    ld e,a ; store provisional biased exponent

; ; DEBUG
;     ld a,e
;     call printDecS8
;     call printNewLine
; ; END DEBUG

; normalise the result and adjust biased exponent
@norm_loop:
    dec e ; decrement biased exponent
    add hl,hl ; left shift uhl
    jr nc,@norm_loop

; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     ld a,e
;     call printDecS8
;     call printNewLine
; ; END DEBUG

 ; check for subnormal product 
    ld a,e
    cp 1
    jp p,@normal_product

; SUBNORMAL PRODUCT
@rot_subnorm:


    jr @prep_rounding

; NORMAL PRODUCT
@normal_product:
; rotate product left twice *with* carry
    xor a
    add hl,hl
    adc a,a
    add hl,hl
    adc a,a
    ld l,a
; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     call printNewLine
; ; END DEBUG

; put GRS bits into d and mantissa bits into hl 
    ld d,h
    ld h,l
    dec sp
    push hl
    inc sp 
    pop af
    ld l,a

; now subnormal and normal products have same alignment:
;      hlu       h       l
; C 76543210 76543210 76543210
; 8 76543210 GRS00000 00000I98
@prep_rounding:
; ; DEBUG
;     call printHexUHL
;     call printBinUHL
;     call printNewLine
; ; END DEBUG

; mask out everything in h except the mantissa bits we're keeping *plus* the implied 1 if normal
    ld a,%00000111
    and h
    ld h,a
; zero hlu
    dec hl
    inc.s hl
;
; now hl is a 16-bit integer with d holding the GRS bits:
;      h       l         d
; C 76543210 76543210 76543210
; x 00000I98 76543210 GRS00000

; do the rounding
; set sticky bit
    ld a,d
    and %00011111
    jr nz,@set_sticky  ; If there are any bits set in the lower 5 bits of d, set sticky
    
    ; If we're here, check our saved LSB (in C) for any sticky bits
    ld a,c
    and a             ; Set flags based on value in C
    jr z,@F           ; If C is zero, no need to set sticky
    
@set_sticky:
    set 5,d           ; set sticky bit
@@:
; now test GRS bits for rounding
    ld a,d
    and %11100000

    cp %10000000

    jp m,@set_sign_exp ; no rounding needed
    jr nz,@round_up ; same as jp p in this case

@round_to_even:
    bit 0,l

;     ; call printNewLine
;     ; call dumpFlags
;     ; call printBin8
;     ; call printNewLine
    
    jr z,@set_sign_exp ; no rounding needed
@round_up:
    inc hl
    bit 3,h ; check carry out of implied 1
    jr z,@set_sign_exp ; no carry
    SRL H ; shift hl down one 
    RR L
    inc e ; and increment the exponent

@set_sign_exp:
    ; call printHexUHL
    ; call printBinUHL
    ; call printBin8
    ; call printNewLine

; determine sign of product
    res 7,h ; clear sign bit
    pop af ; bit 7 of a is the sign of the product
    or h
    ld h,a
; set the exponent
    ld (ix+12),e ; DEBUG write biased exponent to file out buffer
    res 2,h ; clear implied 1 of mantissa
    ld a,e
    rla
    rla
    or h
    ld h,a
    ret   
@de_zero:
    pop de ; dummy pop to balance stack
@hl_zero:
    pop de ; dummy pop to balance stack
    ret 
; end float16_smul_dev

; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af, de
float16_smul:
; determine sign of result and stack it
    ld a,h
    and %10000000
    xor d
    and %10000000
    push af ; stack the sign
; unpack hl
    push de ; TODO: figure out why DE gets stomped here
    call float16_unpack
    pop de ; restore de TODO: figure out why DE gets stomped above
    jr c,@hl_zero
    push af ; stack the true exponent
; unpack de
    ex de,hl
    call float16_unpack
    jr c,@de_zero
    push af ; stack the true exponent
; multiply the mantissae
    call umul24 ; TODO: a 11x11->22 multiply would be more efficient
; normalise the result
    ld a,24 ; number of bits in uhl
@norm_loop:
    add hl,hl ; left shift uhl
    jr c,@F ; loop until first non-zero mantissa bit shifts into carry ...
    dec a
    jr nz,@norm_loop ; ... or we run out of bits
@@: ; compute product's provisional biased exponent prior to rounding
    pop de ; d = true exponent of de
    add a,d
    pop de ; d = true exponent of hl
    add a,d
    sub a,6 ; biased exponent
; check for subnormal product
    cp 1
    jp p,@round_normal
    ld de,1 ; accumulator for mantissa bits
    add 9
@loop:
    add hl,hl
    ex de,hl
    adc hl,hl
    ex de,hl
    dec a
    jr nz,@loop
    ex de,hl
    jr @zero_uhl
@round_normal:
; apply rounding to the normalised result
    ld de,0x002000
    add hl,de
    adc a,0 ; carry to exponent
    ld (ix+12),a ; DEBUG write biased exponent to file out buffer
; rotate bottom 2 mantissa bits into hlu
; and top two mantissa bits into a
@rotate:
    add hl,hl
    adc a,a
    add hl,hl
    adc a,a
    ld h,a ; exponent and top 2 bits of mantissa to h
@rearrange: 
; hlu -> a -> l
    dec sp
    push hl
    inc sp 
    pop af
    ld l,a ; bottom 8 bits of mantissa to l
@zero_uhl:
    dec hl
    inc.s hl
; determine sign of product
    res 7,h ; clear sign bit
    pop af ; bit 7 of a is the sign of the product
    or h
    ld h,a
    ret   
@de_zero:
    pop de ; dummy pop to balance stack
@hl_zero:
    pop de ; dummy pop to balance stack
    ret 
; end float16_smul

; compute the true exponent of a subnormal float16
; inputs: hl is the subnormal float16 mantissa
; outputs: hl is the normalised float16, a is the true exponent
; destroys: flags
float16_norm_sub:
    ld a,1 ; initialize exponent
@norm_loop:
    bit 2,h ; test bit 10 of hl
    ret nz ; return if if set
    add hl,hl ; left shift uhl
    dec a ; dec exponent
    jr @norm_loop ; loop until first non-zero mantissa bit shifts into bit 10 of hl
; end float16_norm_sub

; unpack the sign, exponent, and mantissa of a float16
; inputs: hl is the float16 to unpack
; outputs: a is the true exponent, hl is the normalised mantissa
;          sign and zero flags are correctly (re)set, carry set if hl is +/-zero
float16_unpack:
; get hl's stored exponent
    ld a,h
    and %01111100
    jr nz,@is_nor ; non-zero exponent means normal number
; check for zero or -zero
    SIGN_HL ; get the 16-bit sign of hl
    scf ; assume zero result
    ret z ; result is zero so nothing more to do
    or l ; test l for zero (a is zero)
    jr nz,@is_sub ; number is subnormal
    ld a,h
    add a,a ; sets carry and zero flags if hl is -zero
    ret z ; result is -zero so nothing more to do
@is_sub:
    res 7,h ; clear sign bit
    call float16_norm_sub ; number is subnormal
    or a ; clear carry indicating non-zero result
    ret
@is_nor: ; compute hl's true exponent
    srl a
    srl a
    sub a,15
; put the explicit 1 into the mantissa and (re)set sign flag
    set 2,h
    SIGN_HL
    push af ; stack sign the true exponent
; mask out everything but the top three bits of hl's mantissa
    ld a,h
    and %00000111
    ld h,a
    pop af ; restore the true exponent
    scf ; set carry ...
    ccf ; ... then reset it indicating non-zero result
    ret
; end float16_unpack

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
    or a ; clear carry
    ld hl,0
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

; zero hlu
    dec hl
    inc.s hl

; handle sign
    pop af ; restore sign flag
    ret p ; already positive
    set 7,h ; set sign negative

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
    ; ld h,a ; moved down

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

table: blkl 256,0

make_table:
    ld ix,table ; pointer
    ld b,0 ; loop counter
@loop:
    call prng24 ; hl = random number
    ld (ix),hl ; store it
    lea ix,ix+3 ; next entry
    djnz @loop ; loop until b == 0
    ret

time_fixed24_to_float16:
    call prt_stopwatch_irq_init

    call prt_stopwatch_set
    ld b,0 ; outer loop counter
@loop:
    push bc ; save outer loop counter
    ld ix,table ; pointer to list of random 24-bit numbers
    ld b,0 ; loop counter
@loop0:
    ld hl,(ix) ; get the next random number
    call fixed24_to_float16
    lea ix,ix+3 ; bump ix to next record
    djnz @loop0
    pop bc ; restore outer loop counter
    djnz @loop
    call prt_stopwatch_stop
    call prt_stopwatch_get
    call printDec
    call printNewLine

    call prt_stopwatch_set
    ld b,0 ; outer loop counter
@loop1:
    push bc ; save outer loop counter
    ld ix,table ; pointer to list of random 24-bit numbers
    ld b,0 ; loop counter
@loop2:
    ld hl,(ix) ; get the next random number
    ld a,8 ; 16.8 fixed point
    call fixed24_to_float16_opt
    lea ix,ix+3 ; bump ix to next record
    djnz @loop2
    pop bc ; restore outer loop counter
    djnz @loop1
    call prt_stopwatch_stop
    call prt_stopwatch_get
    call printDec
    call printNewLine

    ret

compare_fixed24_to_float16:
    ld ix,table ; pointer to list of random 24-bit numbers
    ld b,0 ; loop counter
    ld hl,0
    ld (@errors),hl
@loop:
    ld hl,(ix)
    ld a,8 ; 16.8 fixed point
    call fixed24_to_float16
    push hl ; save result

    ld hl,(ix)
    call fixed24_to_float16_opt
    pop de ; get previous result
    or a ; clear carry
    sbc hl,de ; compare
    jr z,@ok
    ld hl,(@errors)
    inc hl
    ld (@errors),hl
@ok:
    lea ix,ix+3 ; bump ix to next record
    djnz @loop
    call printInline
    asciz "Errors:"
    ld hl,(@errors)
    call printDec
    call printNewLine
@errors: dl 0
