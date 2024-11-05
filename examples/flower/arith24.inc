arith24uaf: ds 6
arith24uhl: ds 6
arith24ubc: ds 6
arith24ude: ds 6
arith24uix: ds 6
arith24uiy: ds 6
arith24usp: ds 6
arith24upc: ds 6

; multiply a signed 24-bit number by an unsigned 8-bit number giving a signed 24-bit result
; uses EZ80 MLT instruction for speed
; operation: UHL * A --> UHL
; destroys: AF, HL
smul24x8:
; make hl positive and store sign flag
	call hlu_abs
	push af
; do the division
    call umul24x8 ; hl = product
; adjust sign of result
	pop af ; sign de
	ret p ; hl was positive, nothing to do
	call neg_hlu ; result is negative
	ret

; unsigned multiplication of a 24-bit and 8-bit number giving a 32-bit result
; uses EZ80 MLT instruction for speed
; operation: UHL * A --> AUHL
; destroys: AF, HL
umul24x8:
	push de ; preserve de
; low byte
	ld e,l
	ld d,a
	mlt de
	ld l,e ; product low byte
	ex af,af' ; save multiplier
	ld a,d ; carry
	ex af,af' ; save carry, restore multiplier
; high byte
	ld e,h
	ld d,a
	mlt de
	ex af,af' ; save multiplier, restore carry
	add a,e ; add carry
	ld h,a ; product middle byte
	ld a,d ; carry
	ex af,af' ; save carry, restore multiplier
; upper byte
	push hl
	inc sp
	pop de ; d = hlu
	dec sp
	ld e,a
	mlt de
	ex af,af' ; restore carry
	adc a,e ; add carry
    ld (@scratch),hl ; 7 cycles
    ld (@scratch+2),a ; 5 cycles
    ld hl,(@scratch) ; 7 cycles
; highest byte
	ld a,0 ; preserve carry flag
	adc a,d ; product highest byte
	pop de ; restore de
	ret
@scratch: ds 3

; unsigned multiplication of two 24-bit numbers giving a 48-bit result
; operation: UHL * UDE --> umul24x24out
umul24x24:
	ld iy,umul24x24out ; point to output buffer
	push bc
	ld bc,0
	ld (iy),bc
	ld (iy+3),bc
	pop bc

; STEP 1: UHL * E
	ld a,e
	push hl
	call umul24x8
	ld (iy+0),hl
	ld (iy+3),a

; STEP 2: UHL * D
	pop hl
	push hl
	ld a,d
	call umul24x8
	call @accumulate

; STEP 3: UHL * DEU
	pop hl
	push de
	inc sp
	pop af
	dec sp
	call umul24x8

@accumulate:
	inc iy
; highest byte of product to carry
	ld (iy+3),a
; low byte of product
	ld a,l
	add a,(iy+0)
	ld (iy+0),a
; high byte of product
	ld a,h
	adc a,(iy+1)
	ld (iy+1),a
; uppper byte of product
	push hl
	inc sp
	pop hl
	dec sp
	ld a,h
	adc a,(iy+2)
	ld (iy+2),a
; carry
	ld a,0 ; preserve flags
	adc a,(iy+3)
	ld (iy+3),a
	ret
umul24x24out: ds 6 ; output buffer

; umul168:	UH.L = UH.L*UD.E (unsigned)
umul168:
	call umul24x24
	ld hl,(iy-1)
	ret

; smul168:	UH.L * UD.E --> UH.L (signed)
smul168:
; make everything positive and store sign flags
	call hlu_abs
	push af
	ex de,hl
	call hlu_abs
	ex de,hl
	push af
; do the division
    call umul168 ; hl = product
; adjust sign of result
	pop af ; sign de
	jp m,@de_neg
	pop af ; sign hl
	ret p ; both positive, nothing to do
@hl_neg:
    call neg_hlu ; de pos, hl neg, result is negative
    ret
@de_neg:
	pop af
	ret m ; both negative, nothing to do
	call neg_hlu ; result is negative
	ret

;------------------------------------------------------------------------
;  arith24.inc 
;  24-bit ez80 arithmetic routines
;  Copyright (c) Shawn Sijnstra 2024
;  MIT license
;
;  This library was created as a tool to help make ez80
;  24-bit native assembly routines for simple mathematical problems
;  more widely available.
;  
;------------------------------------------------------------------------

;------------------------------------------------------------------------
; umul24:	HL = HL*DE (unsigned)
; Preserves AF, BC, DE
; Uses a fast multiply routine.
;------------------------------------------------------------------------
umul24:
	push	DE 
	push	BC
	push	AF	
	push	HL
	pop		BC
    ld	 	a, 24 ; No. of bits to process 
    ld	 	hl, 0 ; Result
umul24_lp:
	add	hl,hl
	ex	de,hl
	add	hl,hl
	ex	de,hl
	jr	nc,umul24_nc
	add	hl,bc
umul24_nc: 
	dec	a
	jr	nz,umul24_lp
	pop	af
	pop	bc
	pop	de
	ret

;------------------------------------------------------------------------
; udiv24
; Unsigned 24-bit division
; HLU / DEU --> DEU rem HLU
; Uses AF BC DE HL
; Uses Restoring Division algorithm
;------------------------------------------------------------------------

udiv24:
	push	hl
	pop		bc	;move dividend to BCU
	ld		hl,0	;result
	and		a
	sbc		hl,de	;test for div by 0
	ret		z		;it's zero, carry flag is clear
	add		hl,de	;HL is 0 again
	ld		a,24	;number of loops through.
udiv1:
	push	bc	;complicated way of doing this because of lack of access to top bits
	ex		(sp),hl
	scf
	adc	hl,hl
	ex	(sp),hl
	pop	bc		;we now have bc = (bc * 2) + 1

	adc	hl,hl
	and	a		;is this the bug
	sbc	hl,de
	jr	nc,udiv2
	add	hl,de
;	dec	c
	dec	bc
udiv2:
	dec	a
	jr	nz,udiv1
	scf		;flag used for div0 error
	push	bc
	pop		de	;remainder
	ret


; UH.L / UD.E --> UD.E rem UHL (unsigned)
; perform unsigned division of 16.8 fixed place values
; with an unsigned 16.8 fixed place result and 24-bit remainder
udiv168:
; back up divisor
	ld (@ude),de
; get the 16-bit integer part of the quotient
    call udiv24 ; de = quotient, hl = remainder
; load quotient to upper three bytes of output
    ld (div168_out+1),de
@div256:
; multiply remainder by 256
	hlu_mul256
; skip fractional computation if remainder is zero
    sign_hlu
    jr nz,@div_frac
    xor a
    jr @write_frac
; now divide the shifted remainder by the divisor
@div_frac:
	ld de,(@ude) ; get back divisor
    call udiv24 ; de = quotient, hl = remainder
; load low byte of quotient to low byte of output
    ld a,e
@write_frac:
    ld (div168_out),a
; load de with return value
    ld de,(div168_out)
; load a with any overflow
    ld a,(div168_out+3)
    ret ; ud.e is the 16.8 result
@ude: ds 6
div168_out: ds 4 ; the extra byte is for overflow

; UH.L / UD.E --> UD.E (signed) rem UHL (unsigned)
; perform signed division of 16.8 fixed place values
; with a signed 16.8 fixed place result and unsigned 24-bit remainder
sdiv168:
; make everything positive and store sign flags
	call hlu_abs
	push af
	ex de,hl
	call hlu_abs
	ex de,hl
	push af
; do the division
    call udiv168 ; de = quotient, hl = remainder
; adjust sign of result
	pop af ; sign de
	jp m,@de_neg
	pop af ; sign hl
	ret p ; both positive, nothing to do
@hl_neg:
    ex de,hl ; hl = quotient, de = remainder
    call neg_hlu ; de pos, hl neg, result is negative
    ex de,hl ; de = negated quotient, hl = remainder
    ret
@de_neg:
	pop af
	ret m ; both negative, nothing to do
    ex de,hl ; hl = quotient, de = remainder
	call neg_hlu ; result is negative
    ex de,hl ; de = negated quotient, hl = remainder
	ret

;------------------------------------------------------------------------
; neg24
; Returns: HLU = 0-HLU
; preserves all other registers
;------------------------------------------------------------------------
neg24:
	push	de
	ex		de,hl
	ld		hl,0
	or		a
	sbc		hl,de
	pop		de
	ret

;------------------------------------------------------------------------
; or_hlu_deu: 24 bit bitwise OR
; Returns: hlu = hlu OR deu
; preserves all other registers
;------------------------------------------------------------------------
or_hlu_deu:
	ld	(bitbuf1),hl
	ld	(bitbuf2),de
	push	de	;preserve DEU
	push	bc	;preserve BCU
	ld		b,3
	ld	hl,bitbuf1
	ld	de,bitbuf1
orloop_24:
	ld	a,(de)
	or	(hl)
	ld	(de),a
	inc	de
	inc	hl
	djnz	orloop_24
	ld	hl,(bitbuf2)
	pop		bc	;restore BC
	pop		de	;restore DE

;------------------------------------------------------------------------
; and_hlu_deu: 24 bit bitwise AND
; Returns: hlu = hlu AND deu
; preserves all other registers
;------------------------------------------------------------------------
and_hlu_deu:
	ld	(bitbuf1),hl
	ld	(bitbuf2),de
	push	de	;preserve DEU
	push	bc	;preserve BCU
	ld		b,3
	ld	hl,bitbuf1
	ld	de,bitbuf1
andloop_24:
	ld	a,(de)
	and	(hl)
	ld	(de),a
	inc	de
	inc	hl
	djnz	andloop_24
	ld	hl,(bitbuf2)
	pop		bc	;restore BC
	pop		de	;restore DE

;------------------------------------------------------------------------
; xor_hlu_deu: 24 bit bitwise XOR
; Returns: hlu = hlu XOR deu
; preserves all other registers
;------------------------------------------------------------------------
xor_hlu_deu:
	ld	(bitbuf1),hl
	ld	(bitbuf2),de
	push	de	;preserve DEU
	push	bc	;preserve BCU
	ld		b,3
	ld	hl,bitbuf1
	ld	de,bitbuf1
xorloop_24:
	ld	a,(de)
	xor	(hl)
	ld	(de),a
	inc	de
	inc	hl
	djnz	xorloop_24
	ld	hl,(bitbuf2)
	pop		bc	;restore BC
	pop		de	;restore DE

;------------------------------------------------------------------------
; shl_hlu: 24 bit shift left hlu by deu positions
; Returns: hlu = hlu << deu
;		   de = 0
; NOTE: only considers deu up to 16 bits. 
; preserves all other registers
;------------------------------------------------------------------------
shl_hlu:
	ld		a,d		;up to 16 bit.
	or		e
	ret		z		;we're done
	add		hl,hl	;shift HLU left
	dec		de
	jr		shl_hlu

;------------------------------------------------------------------------
; shr_hlu: 24 bit shift right hlu by deu positions
; Returns: hlu = hlu >> deu
;		   de = 0
; NOTE: only considers deu up to 16 bits. 
; preserves all other registers
;------------------------------------------------------------------------
shr_hlu:
	ld		(bitbuf1),hl
	ld		hl,bitbuf1+2
shr_loop:
	ld		a,d		;up to 16 bit.
	or		e
	jr		z,shr_done		;we're done
;carry is clear from or instruction
	rr		(hl)
	dec		hl
	rr		(hl)
	dec		hl
	rr		(hl)
	inc		hl
	inc		hl
	dec		de
	jr		shr_loop
shr_done:
	ld		hl,(bitbuf1)	;collect result
	ret

;------------------------------------------------------------------------
; Scratch area for calculations
;------------------------------------------------------------------------
bitbuf1:	dw24	0	;bit manipulation buffer 1
bitbuf2:	dw24	0	;bit manipulation buffer 2

; ========== FROM maths24.inc ==========

; Expects  ADL mode
; Inputs:  UH.L
; Outputs: UH.L is the 16.8 square root
;          UD.E is the difference inputHL-DE^2
;          c flag reset  
sqrt168:
    call sqrt24
    ex de,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ret

; Expects  ADL mode
; Inputs:  HL
; Outputs: DE is the integer square root
;          HL is the difference inputHL-DE^2
;          c flag reset 
sqrt24:
    xor a
    ld b,l
    push bc
    ld b,a
    ld d,a
    ld c,a
    ld l,a
    ld e,a

    ;Iteration 1
    add hl,hl
    rl c
    add hl,hl
    rl c
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 2
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl e
    ld a,e
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 3
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl e
    ld a,e
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 4
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl e
    ld a,e
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 5
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl e
    ld a,e
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 6
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl e
    ld a,e
    sub c
    jr nc,$+6
    inc e
    inc e
    cpl
    ld c,a

    ;Iteration 7
    add hl,hl
    rl c
    add hl,hl
    rl c
    rl b
    ex de,hl
    add hl,hl
    push hl
    sbc hl,bc
    jr nc,$+8
    ld a,h
    cpl
    ld b,a
    ld a,l
    cpl
    ld c,a
    pop hl
    jr nc,$+4
    inc hl
    inc hl
    ex de,hl

    ;Iteration 8
    add hl,hl
    ld l,c
    ld h,b
    adc hl,hl
    adc hl,hl
    ex de,hl
    add hl,hl
    sbc hl,de
    add hl,de
    ex de,hl
    jr nc,$+6
    sbc hl,de
    inc de
    inc de

    ;Iteration 9
    pop af
    rla
    adc hl,hl
    rla
    adc hl,hl
    ex de,hl
    add hl,hl
    sbc hl,de
    add hl,de
    ex de,hl
    jr nc,$+6
    sbc hl,de
    inc de
    inc de

    ;Iteration 10
    rla
    adc hl,hl
    rla
    adc hl,hl
    ex de,hl
    add hl,hl
    sbc hl,de
    add hl,de
    ex de,hl
    jr nc,$+6
    sbc hl,de
    inc de
    inc de

    ;Iteration 11
    rla
    adc hl,hl
    rla
    adc hl,hl
    ex de,hl
    add hl,hl
    sbc hl,de
    add hl,de
    ex de,hl
    jr nc,$+6
    sbc hl,de
    inc de
    inc de

    ;Iteration 11
    rla
    adc hl,hl
    rla
    adc hl,hl
    ex de,hl
    add hl,hl
    sbc hl,de
    add hl,de
    ex de,hl
    jr nc,$+6
    sbc hl,de
    inc de
    inc de

    rr d
    rr e
    ret