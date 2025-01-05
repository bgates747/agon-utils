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
    include "files.inc"
    include "fixed168.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_buffered_api.inc"
    include "vdu_fonts.inc"
    include "vdu_plot.inc"
    include "vdu_sound.inc"

; APPLICATION INCLUDES
    include "music.inc"
    include "debug.inc"

; --- MAIN PROGRAM FILE ---
main:
    call vdu_clear_all_buffers

    call printInline
    asciz "Loading SFX...\r\n"
	call load_sfx_AMBIENT_BEAT70
    call printInline
    asciz "SFX loaded.\r\n"

    call load_command_buffer

@loop:
    call waitKeypress
    cp '\e'
    ret z
    cp '1'
    call z,play_song_temp
    jp @loop
; end main


play_song_temp:
    call printInline
    asciz "Playing song...\r\n"
    ld hl,ch0_buffer
    call vdu_call_buffer

    ; ld hl,BUF_AMBIENT_BEAT70
    ; ld c,0 ; channel 0
    ; ld b,8 ; waveform = sample
    ; call vdu_channel_waveform

    ; ld b,127 ; volume
    ; ld c,0 ; channel 0
    ; ld hl,0 ; frequency (doesn't matter for samples)
    ; ld de,0 ; duration 0 means play whole sample once
    ; call vdu_play_note

    ret


load_command_buffer:
    ld hl,ch0_buffer
    call vdu_clear_buffer

    ld hl,ch0_buffer
    ld bc,@sample_end-@sample
    ld de,@sample
    call vdu_write_block_to_buffer
    ret
@sample: 
; Command 4: Set waveform
; VDU 23, 0, &85, channel, 4, waveformOrSample, [bufferId;]
    .db 23,0,$85                        ; do sound
@channel0:   
    .db 0,4,8 ; channel, command, waveform
@bufferId:    
    .dw BUF_AMBIENT_BEAT70
; Command 0: Play note
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    .db 23,0,$85                        ; do sound
@channel1:    
    .db 0,0,127                ; channel, volume
    .dw 0 
@duration:                              ; freq (tuneable samples only)
    .dw 0x0000                        ; duration
@sample_end: