table: blkl 256,0

make_table:
    ld ix,table ; pointer
    ld b,0 ; loop counter
@loop:
    call prng24 ; hl = random number
    ld (ix),hl ; store it
    ; call printHex24
    ; call printNewLine
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

fixed24_to_float16_test:
    ; ld hl,15*256 ; 15.0 -> 0x4B80
    ; ld hl,0x000180 ; 1.5 -> 0x3e00
    ; ld hl,0xFFFE80 ; -1.5 -> 0xbe00
    ; ld hl,0x7FFFFF ; 32767.99609375 -> 0x7800
    ; ld hl,0x800000 ; 32768.0 (unsigned) -> 0x7800
    ; ld hl,0x7FFF00 ; 32767.0 (signed) -> 0x7800
    ; ld hl,0x0000FF ; 0.99609375 -> 0x3F00
    ; ld hl,0xFFFFFF ; 65535.99609375 -> 0x7C00 (unsigned)
    ; ld hl,0x016698 ; 358.59375 -> 0x5D9A
    ld hl,0xFE9968 ; -358.59375 -> 0xDD9A

    ld a,8 ; 16.8 fixed point

    call fixed24_to_float16
    call dumpRegistersHex 
    ret
; end fixed24_to_float16_test

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
