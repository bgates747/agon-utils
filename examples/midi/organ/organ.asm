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

str_version: db "0.0.1.alpha",0

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
    include "organ/organ_channels.asm"
    include "organ/organ_drawbars.asm"
    include "organ/organ_tonewheels.asm"

    include "organ/organ_notes_bank_1.asm"
    include "organ/organ_notes_bank_2.asm"
    include "organ/organ_notes_bank_3.asm"
    include "organ/organ_notes_bank_4.asm"

master_volume: db 127
hammer_curr: ds 17
hammer_last: ds 17
hammer_cmd: ds 17

cmd_frequency: equ frequency0-cmd0
cmd_volume: equ volume0-cmd0
cmd_bytes: equ cmd1-cmd0
notes_played: db 0
str_channels_playing: db "Channels playing: ",0

; ###############################################
; Main loop
; ###############################################

main:
    call vdu_home_cursor
    ld hl,str_version
    call printString
    call printNewline

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

; advance vibrato value
    ld hl,vibrato_lut
    ld a,(vibrato_step)
    inc a
    and 63 ; modulo 64
    ld (vibrato_step),a
    ld e,a
    ld d,3 ; three bytes per lut entry
    mlt de
    add hl,de
    ld hl,(hl)
    ld (vibrato_value),hl

; set tonewheel drawbar multipliers to 0
    xor a
    ld b,84 ; number of tonewheels
    ld ix,tonewheel_frequencies+2
@loop_tonewheels:
    ld (ix),a
    lea ix,ix+4 ; four bytes per record
    djnz @loop_tonewheels

; check key presses
	MOSCALL mos_getkbmap

; quit if escape key pressed
; 113 Escape
    bit 0,(ix+14)
    jp nz,main_exit

; display the virtual keys table
    push ix
    pop hl
    ld a,17
    call dumpMemoryHex

; set the drawbar values according to the keys pressed
    call set_drawbars

; set channels to play according to the keys pressed
    call organ_notes_bank_1
    call organ_notes_bank_2
    call organ_notes_bank_3
    call organ_notes_bank_4

; set channel volumes according to the activated tonewheels
    call set_volumes

; print the number of channels playing
    ld hl,str_channels_playing
    call printString
    ld a,32 ; number of channels 
    sub c ; subtract remaining channel loop counter
    ld hl,0 ; make sure deu is 0
    ld l,a ; hl = number of channels playing
    call printDec
    ; call printNewline
    ; ld hl,_printDecBuffer
    ; ld a,9
    ; call dumpMemoryHex

; play the notes
    call play_notes

; wait a tick
;     call vdu_flip
    call vdu_vblank

    jp main

main_exit:
; cleanup and exit
    ld a,0
    call vdu_set_screen_mode
    ret