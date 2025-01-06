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

    ; call init
    ; call main
    call temp

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

temp:
; ; TEMPORARY - WORKS
; 	call load_sfx_AMBIENT_BEAT70
;     call sfx_play_AMBIENT_BEAT70
;     ret
; ; END TEMPORARY

; TEMPORARY - WORKS
	ld hl,BUF_AMBIENT_BEAT70
	ld iy,FAMBIENT_BEAT70
    call vdu_load_buffer_from_file

; ; vdu_buffer_to_sound:
;     ld hl,@buf2sound         
;     ld bc,@buf2sound_end-@buf2sound
;     rst.lil $18    
; ; end vdu_buffer_to_sound 

; ; vdu_play_sfx:
; 	ld hl,@play_sample
;     ld bc,@play_sample_end-@play_sample
;     rst.lil $18
; ; end vdu_play_sfx

    ld hl,cmd0_buffer
    ld bc,@play_sample_end-@buf2sound
    ld de,@buf2sound
    call vdu_write_block_to_buffer

    ld hl,cmd0_buffer
    call vdu_call_buffer
    ret

; vdu_buffer_to_sound command string
@buf2sound: 
    db 23,0,0x85 ; vdu sound command header
    db 0x00 ; channel (ignored)
    db 0x05 ; buffer to sound command
    db 0x02 ; command 2 create sample
    dw BUF_AMBIENT_BEAT70
    db 0+8 ; 0 = 8-bit signed PCM mono, 8 = sample rate argument follows
    dw sample_rate
@buf2sound_end:

; vdu_play_sfx command string
@play_sample: 
; Command 4: Set waveform
; VDU 23, 0, &85, channel, 4, waveformOrSample, [bufferId;]
    db 23,0,$85 ; vdu sound command header  
    db 0 ; channel
    db 4 ; set waveform command
    db 8 ; waveform 8 = sample
    dw BUF_AMBIENT_BEAT70 ; sample bufferId
; Command 0: Play note
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    db 23,0,$85 ; vdu sound command header
    db 0 ; channel
    db 0 ; play note command
    db 127  ; volume 127 = max
    dw 0 ; frequency (relevant only for tuneable samples)
    dw 0 ; duration (ms), zero means play one time in full
@play_sample_end:
; END TEMPORARY
; end temp

; --- MAIN PROGRAM FILE ---
init:
; initialize channel command buffers
    ld hl,cmd0_buffer
    ld de,ch0_buffer
    ld c,0 ; channel 0
    call load_command_buffer

    ld hl,cmd1_buffer
    ld de,ch1_buffer
    ld c,1 ; channel 1
    call load_command_buffer

    ret
; end init

main:
@loop:
    call waitKeypress
    cp '\e'
    ret z
    cp '1'
    call z,play_song
    jp @loop
; end main

; stream a song from the SD card
; inputs: hl = pointer to filename
; requirements: the file must be 8-bit signed PCM mono sampled at 15360 Hz
; uses: sound channels 0 and 1, buffers 0x3000 and 0x3001
    align 256 ; align to 256-byte boundary (may be helpful ... or not)
song_data: blkw 8192,0 ; buffer for sound data
ch0_buffer: equ 0x3000
cmd0_buffer: equ 0x3001
ch1_buffer: equ 0x3002
cmd1_buffer: equ 0x3003
play_song:
    call printInline
    asciz "Playing song...\r\n"
; TEMPORARY
    ld hl,FAMBIENT_BEAT70
; END TEMPORARY

; open the file in read mode
; Open a file
; HLU: Filename
;   C: Mode
; Returns:
;   A: Filehandle, or 0 if couldn't open
	ld c,fa_read
    MOSCALL mos_fopen
    ld (@filehandle),a

; initialize channel flip-flop
    ld a,1
    push af

@read_file:

; Read a block of data from a file
;   C: Filehandle
; HLU: Pointer to where to write the data to
; DEU: Number of bytes to read
; Returns:
; DEU: Number of bytes read
    ld a,(@filehandle)
    ld c,a
    ld hl,song_data
    ld de,256
    MOSCALL mos_fread

; test de for zero bytes read
    ld hl,0
    xor a ; clear carry
    sbc hl,de
    jp z,@close_file

; load a vdu buffer from local memory
; inputs: hl = bufferId ; bc = length ; de = pointer to data
    ld hl,ch0_buffer
    pop af ; flip-flop
    inc a
    and 1
    ld l,a
    push af ; save flip-flop
    push hl ; sample bufferId
    push de ; chunksize
    pop bc
    ld de,song_data
    call vdu_load_buffer
    call vdu_vblank ; wait for vblank
    pop hl
    inc l ; play commmand bufferId

; DEBUG
    call DEBUG_PRINT
    CALL DEBUG_WAITKEYPRESS
; END DEBUG

    call vdu_call_buffer

; read the next block
    jp @read_file

; close the file
@close_file:
    pop af ; dummy pop to balance stack
    ld a,(@filehandle)
    MOSCALL mos_fclose
    ret

@ch0_play:
    db 23,0,0x85
    db 0   ; channel 0
    db 0   ; play note command
    db 127 ; volume
    dw 0   ; frequency (relevant only for tuneable samples)
    dw 0   ; duration - 0 means play full duration one time
@ch0_play_end:

@ch1_play:
    db 23,0,0x85
    db 1   ; channel 1
    db 0   ; play note command
    db 127 ; volume
    dw 0   ; frequency (relevant only for tuneable samples)
    dw 0   ; duration - 0 means play full duration one time
@ch1_play_end:


@filehandle: db 0 ; file handle
@fil: dl 0 ; pointer to FIL struct

@chunkpointer: dl 0 ; pointer to current chunk

; File information structure (FILINFO)
@filinfo:
@filinfo_fsize:    blkb 4, 0   ; File size (4 bytes)
@filinfo_fdate:    blkb 2, 0   ; Modified date (2 bytes)
@filinfo_ftime:    blkb 2, 0   ; Modified time (2 bytes)
@filinfo_fattrib:  blkb 1, 0   ; File attribute (1 byte)
@filinfo_altname:  blkb 13, 0  ; Alternative file name (13 bytes)
@filinfo_fname:    blkb 256, 0 ; Primary file name (256 bytes)


; load a sound effect command buffer
; inputs: hl = command bufferId, de = sound sample bufferId, c = audio channel
load_command_buffer:
    ld a,c
    ld (@channel0),a
    ld (@channel1),a
    ld (@bufferId),de
    ld a,23
    ld (@bufferId+2),a

    push hl
    call vdu_clear_buffer

    pop hl
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
    .dw 0x0000 ; bufferId of containing the sound sample
; Command 0: Play note
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    .db 23,0,$85                        ; do sound
@channel1:    
    .db 0,0,127                ; channel, volume
    .dw 0 
@duration:                              ; freq (tuneable samples only)
    .dw 0x0000                        ; duration
@sample_end: