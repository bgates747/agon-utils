get_keys:
; point ix at keyboard matrix
    MOSCALL mos_getkbmap

; reset a to no key pressed
    xor a

; 17 Q
    bit 0,(ix+2)
    jr z,@F
    ld a,1
@@:

; 34 W
    bit 1,(ix+4)
    jr z,@F
    ld a,2
@@:

; 35 E
    bit 2,(ix+4)
    jr z,@F
    ld a,3
@@:

; 52 R
    bit 3,(ix+6)
    jr z,@F
    ld a,4
@@:

; 36 T
    bit 3,(ix+4)
    jr z,@F
    ld a,5
@@:

; 69 Y
    bit 4,(ix+8)
    jr z,@F
    ld a,6
@@:

; 54 U
    bit 5,(ix+6)
    jr z,@F
    ld a,7
@@:

; 38 I
    bit 5,(ix+4)
    jr z,@F
    ld a,8
@@:

; 55 O
    bit 6,(ix+6)
    jr z,@F
    ld a,9
@@:

; 56 P
    bit 7,(ix+6)
    jr z,@F
    ld a,10
@@:

; 57 LeftBracket
    bit 0,(ix+7)
    jr z,@F
    ld a,11
@@:

; 89 RightBracket
    bit 0,(ix+11)
    jr z,@F
    ld a,12
@@:

; test for key pressed
    or a
    jr nz,@play ; if key pressed, play note

; otherwise test for note playing and stop it
    ld a,(is_playing)
    or a
    call nz,stopSound
    ret

@play:
    ld hl,last_played
    add a,59 ; 60 is middle C
    cp (hl) ; compare with last note played
    ret z ; same as last, do nothing

    ld (note),a ; midi note number
    ld (hl),a ; save note played

    jp startSound ; ... and return to caller from there

last_played: db 0