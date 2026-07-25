; AGNB 0.2 audio loader
; =====================
;
; The generic RIFF/AGNB file, chunk, bounds, streaming, buffer-clear, buffer-
; load, and buffer-consolidation routines remain in agnb.inc. This file adds
; the audio-specific record path for:
;
;     LIST BUFR
;       BHDR  u16 bufferId
;       AUDI  u8 vdpFormat=0x09; u16 sampleRate
;       DATA  unsigned 8-bit mono PCM bytes
;
; AUDI format 0x09 means VDP base format 1 (unsigned 8-bit mono) with bit 3
; set to record that an explicit u16 sample rate follows. vdu_buffer_to_sound
; accepts the base format and adds bit 3 itself, so finalization masks it off.

agnb_audio_version_major:  equ 0
agnb_audio_version_minor:  equ 2

agnb_audi_format:          equ 0 ; u8 VDP sample format byte
agnb_audi_sample_rate:     equ 1 ; u16 Hz
agnb_audi_payload_size:    equ 3

agnb_audio_vdp_format:     equ 0x09 ; unsigned 8-bit mono + sample rate follows

agnb_id_audi:              db "AUDI"

agnb_audio_filename:
    asciz "sfx.agnb"

; Normalized metadata retained until DATA has been validated and streamed.
agnb_audio_meta_bufferId:  equ 0 ; u16 writer-specified VDP bufferId
agnb_audio_meta_format:    equ 2 ; u8 VDP format; version 0.2 requires 0x09
agnb_audio_meta_rate:      equ 3 ; u16 sample rate in Hz
agnb_audio_meta_data_size: equ 5 ; u32 DATA payload size
agnb_audio_meta_size:      equ 9

agnb_audio_metadata:
    blkb agnb_audio_meta_size,0

; Open sfx.agnb, load every valid audio record at its explicit bufferId, play
; it once, and wait for a keypress before advancing to the next record.
; outputs: A=0/Z after the complete container; error code/NZ on failure
; destroys: AF, BC, DE, HL, IX
agnb_load_audio:
    ld de,agnb_audio_filename
    call agnb_open
    ret nz

    call agnb_read_riff_header
    jr nz,@load_error
    call agnb_read_audio_vers
    jr nz,@load_error

@next_record:
; Stop only at the exact declared RIFF boundary.
    ld a,(agnb_state+agnb_state_file_offset+3)
    ld hl,agnb_state+agnb_state_riff_end+3
    cp (hl)
    jr c,@read_record
    jr nz,@bad_bounds
    ld hl,(agnb_state+agnb_state_file_offset)
    ld de,(agnb_state+agnb_state_riff_end)
    or a
    sbc hl,de
    jr z,@success
    jr nc,@bad_bounds

@read_record:
    call agnb_read_audio_buffer_list
    jr nz,@load_error
    call agnb_stream_data
    jr nz,@load_error
    call agnb_finalize_audio
    jr nz,@load_error

; Duration zero means play the complete sample exactly once. waitKeypress is
; the same simple application-test idiom used elsewhere in this repository.
    ld hl,(agnb_metadata+agnb_meta_bufferId)
    dec hl
    inc.s hl ; preserve the u16 bufferId and clear HLU
    ld bc,0
    call vdu_play_sfx
    call waitKeypress

    call agnb_finish_buffer_list
    jr nz,@load_error
    jr @next_record

@bad_bounds:
    ld a,agnb_error_bounds
    ld (agnb_last_error),a
@load_error:
; Preserve the parser/transport error while still closing the file.
    push af
    call agnb_close
    pop af
    ld (agnb_last_error),a
    or a
    ret

@success:
    jp agnb_close

; Read and validate the single VERS chunk for the provisional audio layout.
agnb_read_audio_vers:
    ld ix,agnb_state+agnb_state_riff_end
    call agnb_read_chunk_header
    ret nz

    ld hl,agnb_header+agnb_chunk_id
    ld de,agnb_id_vers
    call agnb_compare_fourcc
    jp nz,@bad_chunk

    ld hl,(agnb_state+agnb_state_chunk_size)
    ld de,agnb_vers_payload_size
    or a
    sbc hl,de
    jr nz,@bad_version
    ld a,(agnb_state+agnb_state_chunk_size+3)
    or a
    jr nz,@bad_version

; Read the two-byte payload and two required zero padding bytes.
    ld bc,4
    ld de,agnb_header
    call agnb_read_exact
    ret nz
    ld a,(agnb_header+agnb_vers_major)
    cp agnb_audio_version_major
    jr nz,@bad_version
    ld a,(agnb_header+agnb_vers_minor)
    cp agnb_audio_version_minor
    jr nz,@bad_version
    ld a,(agnb_header+2)
    or a
    jr nz,@bad_chunk
    ld a,(agnb_header+3)
    or a
    jr nz,@bad_chunk
    xor a
    ld (agnb_last_error),a
    ret

@bad_version:
    ld a,agnb_error_version
    jr @error
@bad_chunk:
    ld a,agnb_error_chunk
@error:
    ld (agnb_last_error),a
    or a
    ret

; Parse one LIST BUFR and require BHDR, AUDI, DATA in that order. All metadata,
; DATA size, and enclosing bounds validate before any PCM payload is read.
agnb_read_audio_buffer_list:
    xor a
    ld (agnb_record_flags),a

    ld ix,agnb_state+agnb_state_riff_end
    call agnb_read_chunk_header
    ret nz
    ld hl,agnb_header+agnb_chunk_id
    ld de,agnb_id_list
    call agnb_compare_fourcc
    jp nz,@bad_chunk

; LIST must contain its type and three nested chunk headers at minimum.
    ld hl,(agnb_state+agnb_state_chunk_size)
    ld de,3*agnb_chunk_header_size+agnb_list_type_size
    or a
    sbc hl,de
    jp c,@bad_chunk
    ld hl,(agnb_state+agnb_state_chunk_end)
    ld (agnb_state+agnb_state_list_end),hl
    ld a,(agnb_state+agnb_state_chunk_end+3)
    ld (agnb_state+agnb_state_list_end+3),a

    ld bc,agnb_list_type_size
    ld de,agnb_header
    call agnb_read_exact
    ret nz
    ld hl,agnb_header
    ld de,agnb_id_bufr
    call agnb_compare_fourcc
    jp nz,@bad_chunk

; Reuse the proven BHDR reader and mirror its normalized bufferId.
    call agnb_read_bhdr
    ret nz
    ld a,(agnb_metadata+agnb_meta_bufferId)
    ld (agnb_audio_metadata+agnb_audio_meta_bufferId),a
    ld a,(agnb_metadata+agnb_meta_bufferId+1)
    ld (agnb_audio_metadata+agnb_audio_meta_bufferId+1),a

    call agnb_read_audi
    ret nz

; Read and validate DATA header, leaving the PCM payload unread for streaming.
    ld ix,agnb_state+agnb_state_list_end
    call agnb_read_chunk_header
    ret nz
    ld hl,agnb_header+agnb_chunk_id
    ld de,agnb_id_data
    call agnb_compare_fourcc
    jp nz,@bad_chunk

    ld hl,(agnb_state+agnb_state_chunk_size)
    ld (agnb_metadata+agnb_meta_data_size),hl
    ld (agnb_audio_metadata+agnb_audio_meta_data_size),hl
    ld a,(agnb_state+agnb_state_chunk_size+3)
    ld (agnb_metadata+agnb_meta_data_size+3),a
    ld (agnb_audio_metadata+agnb_audio_meta_data_size+3),a
    call agnb_validate_audio_data
    ret nz

    ld a,(agnb_record_flags)
    or 1<<agnb_record_has_data
    ld (agnb_record_flags),a
    xor a
    ld (agnb_last_error),a
    ret

@bad_chunk:
    ld a,agnb_error_chunk
    ld (agnb_last_error),a
    or a
    ret

; Read the three-byte AUDI payload plus its required zero padding byte.
agnb_read_audi:
    ld ix,agnb_state+agnb_state_list_end
    call agnb_read_chunk_header
    ret nz
    ld hl,agnb_header+agnb_chunk_id
    ld de,agnb_id_audi
    call agnb_compare_fourcc
    jr nz,@bad_chunk

    ld hl,(agnb_state+agnb_state_chunk_size)
    ld de,agnb_audi_payload_size
    or a
    sbc hl,de
    jr nz,@bad_metadata
    ld a,(agnb_state+agnb_state_chunk_size+3)
    or a
    jr nz,@bad_metadata

    ld bc,4
    ld de,agnb_header
    call agnb_read_exact
    ret nz
    ld a,(agnb_header+agnb_audi_format)
    cp agnb_audio_vdp_format
    jr nz,@bad_metadata
    ld (agnb_audio_metadata+agnb_audio_meta_format),a

; Sample rate must be nonzero. Its u16 storage already enforces the VDP limit.
    ld a,(agnb_header+agnb_audi_sample_rate)
    ld hl,agnb_header+agnb_audi_sample_rate+1
    or (hl)
    jr z,@bad_metadata
    ld a,(agnb_header+agnb_audi_sample_rate)
    ld (agnb_audio_metadata+agnb_audio_meta_rate),a
    ld a,(agnb_header+agnb_audi_sample_rate+1)
    ld (agnb_audio_metadata+agnb_audio_meta_rate+1),a

    ld a,(agnb_header+3)
    or a
    jr nz,@bad_chunk
    ld a,(agnb_record_flags)
    or 1<<agnb_record_has_imag ; descriptor-present bit is shared with IMAG
    ld (agnb_record_flags),a
    xor a
    ld (agnb_last_error),a
    ret

@bad_metadata:
    ld a,agnb_error_metadata
    jr @error
@bad_chunk:
    ld a,agnb_error_chunk
@error:
    ld (agnb_last_error),a
    or a
    ret

; Audio DATA must be nonempty and fit the generic loader's u24 stream counter.
agnb_validate_audio_data:
    ld a,(agnb_audio_metadata+agnb_audio_meta_data_size+3)
    or a
    jr nz,@bad_size
    ld hl,(agnb_audio_metadata+agnb_audio_meta_data_size)
    ld de,0
    or a
    sbc hl,de
    jr z,@bad_size
    xor a
    ld (agnb_last_error),a
    ret
@bad_size:
    ld a,agnb_error_data_size
    ld (agnb_last_error),a
    or a
    ret

; Convert the consolidated buffer to a VDP audio sample using the retained
; writer-specified bufferId, unsigned base format, and explicit sample rate.
agnb_finalize_audio:
    ld hl,(agnb_audio_metadata+agnb_audio_meta_bufferId)
    dec hl
    inc.s hl ; preserve u16 bufferId and clear HLU
    ld de,(agnb_audio_metadata+agnb_audio_meta_rate)
    dec de
    inc.s de ; preserve u16 sample rate and clear DEU
    ld a,(agnb_audio_metadata+agnb_audio_meta_format)
    and $07 ; vdu_buffer_to_sound adds the sample-rate-present bit itself
    call vdu_buffer_to_sound
    xor a
    ld (agnb_last_error),a
    ret
