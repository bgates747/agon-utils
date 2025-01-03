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

    call init
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
    include "files.inc"
    include "fixed168.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_fonts.inc"
    include "vdu_plot.inc"
    include "vdu_sound.inc"

; APPLICATION INCLUDES
    include "music.inc"

; --- MAIN PROGRAM FILE ---
init:
; load sound effects files
    call printInline
    asciz "Loading SFX...\r\n"
    ; call load_sfx_AMBIENT_BEAT70
    ; call load_sfx_SPACE_ADVENTURE
    ; call load_sfx_COME_UNDONE
    call load_sfx_RHIANNON
    ; call load_sfx_AFRICA
    ; call load_sfx_EVERY_BREATH_YOU_TAKE
    call printInline
    asciz "SFX loaded.\r\n"

; ; set sample rate for sound buffers
;     ld b,max_channels ; loop counter
; @rate_loop:
;     push bc ; save loop counter
;     ld hl,15360 ; Hz, for 8-bit PCM mono this is 256 bytes per 1/60th of a second
;     ld c,b ; channel nuber +1
;     dec c ; 0-based index
;     call vdu_set_sample_rate
;     pop bc ; restore loop counter
;     djnz @rate_loop

    ret
; end init

main:


@loop:
    call waitKeypress
    cp '\e'
    ret z
    ; call sfx_play_ambient_beat70
    ; call sfx_play_space_adventure
    cp '1'
    ; call z,sfx_play_come_undone
    ; cp '2'
    call z,sfx_play_rhiannon
    ; cp '3'
    ; call z,sfx_play_africa
    ; cp '4'
    ; call z,sfx_play_every_breath_you_take
    jp @loop
; end main

