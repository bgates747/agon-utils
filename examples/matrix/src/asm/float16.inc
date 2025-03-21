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
@exp_loop:
    add hl,hl ; left shift uhl
    jr c,@F ; loop until first non-zero mantissa bit shifts into carry ...
    dec a
    jr nz,@exp_loop ; ... or we run out of bits
@@: ; compute product's provisional biased exponent prior to rounding
    pop de ; d = true exponent of de
    add a,d
    pop de ; d = true exponent of hl
    add a,d
    sub a,6 ; biased exponent
; apply rounding to the normalised result
    ld de,0x002000
    add hl,de
    adc a,0 ; carry to exponent
    ld (ix+12),a ; store biased exponent

; check for subnormal product
    cp 1
    jp p,@rotate
    ld de,1 ; accumulator for mantissa bits
    ; call printDecS8
    ; call printNewLine
    add 9
    ; call printHexUHL
    ; call printBinUHL
    ; call printDecS8
    ; call printNewLine 
@loop:
    add hl,hl
    ex de,hl
    adc hl,hl

    ; call printHexUHL
    ; call printBinUHL
    ; call printDecS8
    ; call printNewLine 

    ex de,hl
    dec a
    jr nz,@loop
    ex de,hl
    jr @zero_uhl

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

; normalise a subnormal float16 mantissa and compute its true exponent
; inputs: hl is the subnormal float16
; outputs: hl is the normalised float16, a is the true exponent
; modifies: af, hl
float16_norm_sub:
    ld a,-14
@norm_loop:
    add hl,hl ; left shift uhl
    dec a ; bump exponent
    bit 2,h ; test bit 10 of hl
    jr z,@norm_loop ; loop until first non-zero mantissa bit shifts into bit 10 of hl
    ret
; end float16_norm_sub

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
    call float16_norm_sub ; number is subnormal
    or a ; clear carry indicating non-zero result
    ret
@is_nor: ; compute hl's true exponent
    srl a
    srl a
    sub a,15
; put the explicit 1 into the mantissa
    set 2,h
    push af ; stack the true exponent
; mask out everything but the top three bits of hl's mantissa
    ld a,h
    and %00000111
    ld h,a
    pop af ; restore the true exponent
    or a ; clear carry indicating non-zero result
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
