    include "organ/mos_api.asm"

; Command 4: Set waveform
; VDU 23, 0, &85, channel, 4, 8, bufferId;
    MACRO WAVEFORM_SAMPLE channel, buffer_id
    ld hl, @startChannel
    ld bc, @endChannel - @startChannel
    rst.lil $18
    jr @endChannel 
@startChannel: 
    .db 23,0,$85    ; do sound
    .db channel,4,8 ; channel, command, waveform
    .dw buffer_id
@endChannel:
    ENDMACRO

;MOS INITIALIATION 
    .assume adl=1   
    .org 0x040000    

    jp start       

    .align 64      
    .db "MOS"       
    .db 00h         
    .db 01h  

start:              
    push af
    push bc
    push de
    push ix
    push iy

; ###############################################
	call	init			; Initialization code
	call 	main			; Call the main function
; ###############################################

    call cursor_on

exit:
    pop iy                              ; Pop all registers back from the stack
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0                             ; Load the MOS API return code (0) for no errors.

    ret                                 ; Return MOS

; ###############################################
; Initialization
; ###############################################
init:
; enable all the channels
    ld hl, enable_channels_cmd
    ld bc, enable_channels_end - enable_channels_cmd
    rst.lil $18
    jp enable_channels_end
enable_channels_cmd:
    db 23, 0, $85, 3, 8
    db 23, 0, $85, 4, 8
    db 23, 0, $85, 5, 8
    db 23, 0, $85, 6, 8
    db 23, 0, $85, 7, 8
    db 23, 0, $85, 8, 8
    db 23, 0, $85, 9, 8
    db 23, 0, $85, 10, 8
    db 23, 0, $85, 11, 8
    db 23, 0, $85, 12, 8
    db 23, 0, $85, 13, 8
    db 23, 0, $85, 14, 8
    db 23, 0, $85, 15, 8
    db 23, 0, $85, 16, 8
    db 23, 0, $85, 17, 8
    db 23, 0, $85, 18, 8
    db 23, 0, $85, 19, 8
    db 23, 0, $85, 20, 8
    db 23, 0, $85, 21, 8
    db 23, 0, $85, 22, 8
    db 23, 0, $85, 23, 8
    db 23, 0, $85, 24, 8
    db 23, 0, $85, 25, 8
    db 23, 0, $85, 26, 8
    db 23, 0, $85, 27, 8
    db 23, 0, $85, 28, 8
    db 23, 0, $85, 29, 8
    db 23, 0, $85, 30, 8
    db 23, 0, $85, 31, 8
enable_channels_end:

waveform_square: equ 0 ; square wave
waveform_triangle: equ 1 ; triangle wave
waveform_sawtooth: equ 2 ; sawtooth wave
waveform_sine: equ 3 ; sine wave
waveform_noise: equ 4 ; noise wave
waveform_vic_noise: equ 5 ; VIC noise wave
waveform_sample: equ 8 ; PCM sound sample 

waveform: equ waveform_sine

; set waveform for all channels
    ld hl, waveform_channels_cmd
    ld bc, waveform_channels_end - waveform_channels_cmd
    rst.lil $18
    jp waveform_channels_end
waveform_channels_cmd:
    db 23, 0, $85, 0, 4, waveform
    db 23, 0, $85, 1, 4, waveform
    db 23, 0, $85, 2, 4, waveform
    db 23, 0, $85, 3, 4, waveform
    db 23, 0, $85, 4, 4, waveform
    db 23, 0, $85, 5, 4, waveform
    db 23, 0, $85, 6, 4, waveform
    db 23, 0, $85, 7, 4, waveform
    db 23, 0, $85, 8, 4, waveform
    db 23, 0, $85, 9, 4, waveform
    db 23, 0, $85, 10, 4, waveform
    db 23, 0, $85, 11, 4, waveform
    db 23, 0, $85, 12, 4, waveform
    db 23, 0, $85, 13, 4, waveform
    db 23, 0, $85, 14, 4, waveform
    db 23, 0, $85, 15, 4, waveform
    db 23, 0, $85, 16, 4, waveform
    db 23, 0, $85, 17, 4, waveform
    db 23, 0, $85, 18, 4, waveform
    db 23, 0, $85, 19, 4, waveform
    db 23, 0, $85, 20, 4, waveform
    db 23, 0, $85, 21, 4, waveform
    db 23, 0, $85, 22, 4, waveform
    db 23, 0, $85, 23, 4, waveform
    db 23, 0, $85, 24, 4, waveform
    db 23, 0, $85, 25, 4, waveform
    db 23, 0, $85, 26, 4, waveform
    db 23, 0, $85, 27, 4, waveform
    db 23, 0, $85, 28, 4, waveform
    db 23, 0, $85, 29, 4, waveform
    db 23, 0, $85, 30, 4, waveform
    db 23, 0, $85, 31, 4, waveform
waveform_channels_end:

    ld a,3
    call vdu_set_screen_mode

    call cursor_off
    call vdu_cls
    ret

    include "organ/functions.asm"
    include "organ/timer.asm"
    include "organ/maths.asm"
    include "organ/organ_vdu.asm"

master_volume: db 127
hammer_curr: ds 17
hammer_last: ds 17
hammer_cmd: ds 17

; ###############################################
; Main loop
; ###############################################

main:
    call vdu_home_cursor

; set set default volume to 0 for all channels
    xor a
    ld (volume0),a
    ld (volume1),a
    ld (volume2),a
    ld (volume3),a
    ld (volume4),a
    ld (volume5),a
    ld (volume6),a
    ld (volume7),a
    ld (volume8),a
    ld (volume9),a
    ld (volume10),a
    ld (volume11),a
    ld (volume12),a
    ld (volume13),a
    ld (volume14),a
    ld (volume15),a
    ld (volume16),a
    ld (volume17),a
    ld (volume18),a
    ld (volume19),a
    ld (volume20),a
    ld (volume21),a
    ld (volume22),a
    ld (volume23),a
    ld (volume24),a
    ld (volume25),a
    ld (volume26),a
    ld (volume27),a
    ld (volume28),a
    ld (volume29),a
    ld (volume30),a
    ld (volume31),a

    ld iy,play_notes_cmd

    ld a,31 ; 32 channels
main_loop:
    push af
    call dumpRegistersHex
    call vdu_home_cursor
; check key presses
	; MOSCALL mos_getkbmap

; ; increment number of tones being played
;     ld a,127
;     ld (iy+cmd_volume),a
;     ld hl,440 ; A4
;     ld a,l
;     ld (iy+cmd_frequency),a
;     ld a,h
;     ld (iy+cmd_frequency+1),a
;     lea iy,iy+cmd_bytes
;     push iy

; ; play the notes
;     call play_notes

; start playing the next note
    pop af
    ld (play_note_channel),a
    push af
    call play_note

; set a timer delay of 1 second
    ld hl,120
    ld iy,loop_timer
    call timer_set

timer_wait:
    ld iy,loop_timer
    call timer_get
    jp p,timer_wait

; decrement loop counter
    pop af
    dec a
    jp nz,main_loop

; cleanup and exit
main_exit:
    ld a,0
    call vdu_set_screen_mode

; VDU 23, 0, &85, channel, 2, volume
    ld hl,cmdSilent
    ld bc,cmdSilentEnd-cmdSilent
    rst.lil $18
    ret
cmdSilent:  db 23, 0, $85
            db -1 ; channel (all) 
            db 2 ; set volume command
            db 0 ; volume
cmdSilentEnd: 

main_abort:
    pop af ; dumy pop to balance stack
    jp main_exit

loop_timer: ds 6

play_note:
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    ld hl, play_note_cmd
    ld bc, play_note_end - play_note_cmd
    rst.lil $18
    ret
play_note_cmd:
    db 23, 0, $85
play_note_channel: 
    db 0 ; channel
    db 0 ; play note command
    db 127 ; volume
    dw 440 ; frequency
    dw -1 ; duration (infinite)
play_note_end:

max_notes: equ 32
play_notes:

    ld hl,play_notes_cmd
    ld bc,play_notes_end-play_notes_cmd
    rst.lil $18
    ret
play_notes_cmd:

cmd0:         db 23, 0, $85, 0, 3
frequency0:   dw 0 
              db 23, 0, $85, 0, 2
volume0:      db 0

cmd1:         db 23, 0, $85, 1, 3
frequency1:   dw 0 
              db 23, 0, $85, 1, 2
volume1:      db 0

cmd2:         db 23, 0, $85, 2, 3
frequency2:   dw 0 
              db 23, 0, $85, 2, 2
volume2:      db 0

cmd3:         db 23, 0, $85, 3, 3
frequency3:   dw 0 
              db 23, 0, $85, 3, 2
volume3:      db 0

cmd4:         db 23, 0, $85, 4, 3
frequency4:   dw 0 
              db 23, 0, $85, 4, 2
volume4:      db 0

cmd5:         db 23, 0, $85, 5, 3
frequency5:   dw 0 
              db 23, 0, $85, 5, 2
volume5:      db 0

cmd6:         db 23, 0, $85, 6, 3
frequency6:   dw 0 
              db 23, 0, $85, 6, 2
volume6:      db 0

cmd7:         db 23, 0, $85, 7, 3
frequency7:   dw 0 
              db 23, 0, $85, 7, 2
volume7:      db 0

cmd8:         db 23, 0, $85, 8, 3
frequency8:   dw 0 
              db 23, 0, $85, 8, 2
volume8:      db 0

cmd9:         db 23, 0, $85, 9, 3
frequency9:   dw 0 
              db 23, 0, $85, 9, 2
volume9:      db 0

cmd10:         db 23, 0, $85, 10, 3
frequency10:   dw 0 
              db 23, 0, $85, 10, 2
volume10:      db 0

cmd11:         db 23, 0, $85, 11, 3
frequency11:   dw 0 
              db 23, 0, $85, 11, 2
volume11:      db 0

cmd12:         db 23, 0, $85, 12, 3
frequency12:   dw 0 
              db 23, 0, $85, 12, 2
volume12:      db 0

cmd13:         db 23, 0, $85, 13, 3
frequency13:   dw 0 
              db 23, 0, $85, 13, 2
volume13:      db 0

cmd14:         db 23, 0, $85, 14, 3
frequency14:   dw 0 
              db 23, 0, $85, 14, 2
volume14:      db 0

cmd15:         db 23, 0, $85, 15, 3
frequency15:   dw 0 
              db 23, 0, $85, 15, 2
volume15:      db 0

cmd16:         db 23, 0, $85, 16, 3
frequency16:   dw 0 
              db 23, 0, $85, 16, 2
volume16:      db 0

cmd17:         db 23, 0, $85, 17, 3
frequency17:   dw 0 
              db 23, 0, $85, 17, 2
volume17:      db 0

cmd18:         db 23, 0, $85, 18, 3
frequency18:   dw 0 
              db 23, 0, $85, 18, 2
volume18:      db 0

cmd19:         db 23, 0, $85, 19, 3
frequency19:   dw 0 
              db 23, 0, $85, 19, 2
volume19:      db 0

cmd20:         db 23, 0, $85, 20, 3
frequency20:   dw 0 
              db 23, 0, $85, 20, 2
volume20:      db 0

cmd21:         db 23, 0, $85, 21, 3
frequency21:   dw 0 
              db 23, 0, $85, 21, 2
volume21:      db 0

cmd22:         db 23, 0, $85, 22, 3
frequency22:   dw 0 
              db 23, 0, $85, 22, 2
volume22:      db 0

cmd23:         db 23, 0, $85, 23, 3
frequency23:   dw 0 
              db 23, 0, $85, 23, 2
volume23:      db 0

cmd24:         db 23, 0, $85, 24, 3
frequency24:   dw 0 
              db 23, 0, $85, 24, 2
volume24:      db 0

cmd25:         db 23, 0, $85, 25, 3
frequency25:   dw 0 
              db 23, 0, $85, 25, 2
volume25:      db 0

cmd26:         db 23, 0, $85, 26, 3
frequency26:   dw 0 
              db 23, 0, $85, 26, 2
volume26:      db 0

cmd27:         db 23, 0, $85, 27, 3
frequency27:   dw 0 
              db 23, 0, $85, 27, 2
volume27:      db 0

cmd28:         db 23, 0, $85, 28, 3
frequency28:   dw 0 
              db 23, 0, $85, 28, 2
volume28:      db 0

cmd29:         db 23, 0, $85, 29, 3
frequency29:   dw 0 
              db 23, 0, $85, 29, 2
volume29:      db 0

cmd30:         db 23, 0, $85, 30, 3
frequency30:   dw 0 
              db 23, 0, $85, 30, 2
volume30:      db 0

cmd31:         db 23, 0, $85, 31, 3
frequency31:   dw 0 
              db 23, 0, $85, 31, 2
volume31:      db 0


play_notes_end:

cmd_frequency: equ frequency0-cmd0
cmd_volume: equ volume0-cmd0
cmd_bytes: equ cmd1-cmd0
notes_played: db 0
