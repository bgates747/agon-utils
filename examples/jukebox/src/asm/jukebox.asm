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
    include "vdu_buffered_api.inc"
    include "vdu_fonts.inc"
    include "vdu_plot.inc"
    include "vdu_sound.inc"

; APPLICATION INCLUDES
    include "music.inc"
    include "debug.inc"

; --- MAIN PROGRAM FILE ---
init:
    call load_command_buffer
    ret
; end init

ch0_buffer: equ 0x3000
ch1_buffer: equ 0x3001
cmd0_buffer: equ 0x3002
cmd1_buffer: equ 0x3003

main:

; stream a song from the SD card
; inputs: hl = pointer to filename
; requirements: the file must be 8-bit signed PCM mono sampled at 15360 Hz
; uses: sound channels 0 and 1, buffers 0x3000 and 0x3001
play_song:
    call printInline
    asciz "Playing song...\r\n"
; TEMPORARY
    ld hl,FRHIANNON
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
    ld de,256*60
    MOSCALL mos_fread

; test de for zero bytes read
    ld hl,0
    xor a ; clear carry
    sbc hl,de
    jp z,@close_file

; load a vdu buffer from local memory
; inputs: hl = bufferId ; bc = length ; de = pointer to data
    ld a,(@channel)
    inc a
    and 1
    ld (@channel),a
    ld hl,ch0_buffer
    ld l,a
    push hl ; sample bufferId
    call vdu_clear_buffer
    pop hl
    push hl
    push de ; chunksize
    pop bc
    ld de,song_data
    call vdu_load_buffer

    ; call vdu_vblank ; wait for vblank
    ld a,%10000000
    call multiPurposeDelay

    pop hl
    inc l
    inc l ; play commmand bufferId
    call vdu_call_buffer

; read the next block
    jp @read_file

; close the file
@close_file:
    pop af ; dummy pop to balance stack
    ld a,(@filehandle)
    MOSCALL mos_fclose
    ret

@channel: db 0 ; channel number

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


load_command_buffer:
    ld hl,cmd0_buffer
    call vdu_clear_buffer
    ld hl,cmd0_buffer
    ld bc,@cmd0_end-@cmd0
    ld de,@cmd0
    call vdu_write_block_to_buffer

    ld hl,cmd1_buffer
    call vdu_clear_buffer
    ld hl,cmd1_buffer
    ld bc,@cmd1_end-@cmd1
    ld de,@cmd1
    call vdu_write_block_to_buffer
    ret

@cmd0:
; vdu_buffer_to_sound command string
; Command 5: Buffer to sound
    db 23,0,0x85 ; vdu sound command header
    db 0x00 ; channel (ignored)
    db 0x05 ; buffer to sound command
    db 0x02 ; command 2 create sample
    dw ch0_buffer
    db 0+8 ; 0 = 8-bit signed PCM mono, 8 = sample rate argument follows
    dw sample_rate
; vdu_play_sfx command string
; Command 4: Set waveform
; VDU 23, 0, &85, channel, 4, waveformOrSample, [bufferId;]
    db 23,0,$85 ; vdu sound command header  
    db 0 ; channel
    db 4 ; set waveform command
    db 8 ; waveform 8 = sample
    dw ch0_buffer ; sample bufferId
; Command 0: Play note
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    db 23,0,$85 ; vdu sound command header
    db 0 ; channel
    db 0 ; play note command
    db 127  ; volume 127 = max
    dw 0 ; frequency (relevant only for tuneable samples)
    dw 0 ; duration (ms), zero means play one time in full
@cmd0_end:

@cmd1:
; vdu_buffer_to_sound command string
; Command 5: Buffer to sound
    db 23,0,0x85 ; vdu sound command header
    db 0x00 ; channel (ignored)
    db 0x05 ; buffer to sound command
    db 0x02 ; command 2 create sample
    dw ch1_buffer
    db 0+8 ; 0 = 8-bit signed PCM mono, 8 = sample rate argument follows
    dw sample_rate
; vdu_play_sfx command string
; Command 4: Set waveform
; VDU 23, 0, &85, channel, 4, waveformOrSample, [bufferId;]
    db 23,0,$85 ; vdu sound command header  
    db 1 ; channel
    db 4 ; set waveform command
    db 8 ; waveform 8 = sample
    dw ch1_buffer ; sample bufferId
; Command 0: Play note
; VDU 23, 0, &85, channel, 0, volume, frequency; duration;
    db 23,0,$85 ; vdu sound command header
    db 1 ; channel
    db 0 ; play note command
    db 127  ; volume 127 = max
    dw 0 ; frequency (relevant only for tuneable samples)
    dw 0 ; duration (ms), zero means play one time in full
@cmd1_end:
; end load_command_buffers

    align 256 ; align to 256-byte boundary (may be helpful ... or not)
song_data: ; blkw 6556,0 ; buffer for sound data