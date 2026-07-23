; AGNB 0.1 image-container layout
; ===============================
;
; AGNB is a RIFF container. All integer fields are unsigned little-endian.
; Every chunk begins with a four-byte ID and a u32 payload size. The payload
; follows immediately and is padded with zero bytes to a four-byte boundary.
; The stored chunk size excludes its eight-byte header and alignment padding.
;
;     RIFF  u32(file size - 8)  AGNB
;       VERS  size=2
;         u8 major=0
;         u8 minor=1
;       LIST  type=BUFR
;         BHDR  size=2
;           u16 bufferId
;         IMAG  size=5
;           u16 width
;           u16 height
;           u8  format=1        ; RGBA2222
;         DATA  size=width*height
;           u8 pixels[]         ; row-major, no row padding
;
; VERS occurs once before the LIST records. Each version 0.1 LIST BUFR record
; contains exactly BHDR, IMAG, and DATA in that order. The LIST payload starts
; with its four-byte BUFR type, followed by those nested chunks. Readers must
; validate the enclosing RIFF/LIST bounds and the BHDR/IMAG metadata before
; reading or uploading DATA. Chunk traversal advances by:
;
;     8 + ((payload_size + 3) & ~3)
;
; The offsets below are indices from the beginning of the named header or
; payload. RIFF and chunk sizes are u32 values even though ADL registers are
; 24-bit, so their high byte must not be silently discarded during validation.

; RIFF file header: "RIFF", u32 size, "AGNB"
agnb_riff_id:              equ 0
agnb_riff_size:            equ 4
agnb_riff_form:            equ 8
agnb_riff_header_size:     equ 12

; Generic RIFF chunk header: FourCC ID, u32 payload size
agnb_chunk_id:             equ 0
agnb_chunk_size:           equ 4
agnb_chunk_data:           equ 8
agnb_chunk_header_size:    equ 8

; VERS payload
agnb_vers_major:           equ 0
agnb_vers_minor:           equ 1
agnb_vers_payload_size:    equ 2

; LIST BUFR payload
agnb_list_type:            equ 0
agnb_list_chunks:          equ 4
agnb_list_type_size:       equ 4

; BHDR payload
agnb_bhdr_bufferId:        equ 0
agnb_bhdr_payload_size:    equ 2

; IMAG payload
agnb_imag_width:           equ 0
agnb_imag_height:          equ 2
agnb_imag_format:          equ 4
agnb_imag_payload_size:    equ 5

; DATA payload
agnb_data_pixels:          equ 0

; Values supported by the version 0.1 image loader
agnb_version_major:        equ 0
agnb_version_minor:        equ 1
agnb_image_rgba2222:       equ 1


; FourCC constants
; ----------------
; Store each identifier exactly as it appears on disk. agnb_compare_fourcc
; compares one of these tables with four bytes read from the container.

agnb_id_riff:              db "RIFF"
agnb_id_agnb:              db "AGNB"
agnb_id_vers:              db "VERS"
agnb_id_list:              db "LIST"
agnb_id_bufr:              db "BUFR"
agnb_id_bhdr:              db "BHDR"
agnb_id_imag:              db "IMAG"
agnb_id_data:              db "DATA"


; Reader result codes
; -------------------
; Public routines will return A=0 with Z set on success, or one of these
; nonzero values with NZ set on failure. The same value is stored in
; agnb_last_error.

agnb_error_ok:             equ 0
agnb_error_open:           equ 1
agnb_error_read:           equ 2
agnb_error_seek:           equ 3
agnb_error_riff_id:        equ 4
agnb_error_riff_form:      equ 5
agnb_error_version:        equ 6
agnb_error_chunk:          equ 7
agnb_error_bounds:         equ 8
agnb_error_bufferId:       equ 9
agnb_error_metadata:       equ 10
agnb_error_data_size:      equ 11
agnb_error_vdp:            equ 12
agnb_error_eof:            equ 13
agnb_error_not_implemented: equ 255


; FatFS file structure
; --------------------
; The direct ffs_* API needs one caller-owned FIL. Its field indices come from
; mos_api.inc. No FILINFO is needed for opening, reading, seeking, or closing
; the single known container filename.

agnb_fil_size:             equ fil_dir_ptr+3
agnb_fil:
    blkb agnb_fil_size,0


; Reader-state structure
; ----------------------
; RIFF sizes and offsets are u32 and are kept as four bytes even though most
; eZ80 arithmetic is 24-bit. The byte at offset +3 must participate in bounds
; checks and FatFS seeks.

agnb_state_file_size:      equ 0  ; u32 physical size from FIL object
agnb_state_riff_end:       equ 4  ; u32 first byte after RIFF contents
agnb_state_list_end:       equ 8  ; u32 first byte after current LIST payload
agnb_state_chunk_size:     equ 12 ; u32 current chunk payload size
agnb_state_chunk_end:      equ 16 ; u32 first byte after current payload
agnb_state_file_offset:    equ 20 ; u32 current logical read position
agnb_state_bytes_read:     equ 24 ; u32 last read count (high byte normally 0)
agnb_state_size:           equ 28

agnb_state:
    blkb agnb_state_size,0


; Normalized image metadata
; -------------------------
; BHDR and IMAG are copied here and validated completely before DATA is read.

agnb_meta_bufferId:        equ 0  ; u16 writer-specified VDP bufferId
agnb_meta_width:           equ 2  ; u16 pixels
agnb_meta_height:          equ 4  ; u16 pixels
agnb_meta_format:          equ 6  ; u8, version 0.1 requires RGBA2222
agnb_meta_data_size:       equ 7  ; u32 DATA payload size
agnb_meta_size:            equ 11

agnb_metadata:
    blkb agnb_meta_size,0

; Record-validation flags. These are reset at the start of each LIST BUFR.
agnb_record_has_bhdr:      equ 0
agnb_record_has_imag:      equ 1
agnb_record_has_data:      equ 2

agnb_record_flags:         db 0
agnb_last_error:           db agnb_error_ok
agnb_file_is_open:         db 0


; Reusable I/O storage
; --------------------
; The 12-byte buffer is large enough for either the RIFF file header or a
; generic chunk header plus the four-byte LIST type. DATA is streamed through
; the application's existing 8 KiB SRAM filedata area.

agnb_header:
    blkb agnb_riff_header_size,0

agnb_io_buffer:            equ 0xB7E000 ; same onboard SRAM as app filedata
agnb_io_buffer_size:       equ 8192

agnb_filename:
    asciz "images.agnb"


; Reader subroutine interface
; ---------------------------
; These labels establish the intended decomposition and calling contracts.
; They deliberately fail with agnb_error_not_implemented until replaced with
; real code, preventing an incomplete loader from reporting false success.

; Compare two FourCC values.
; inputs:  HL = pointer to first FourCC, DE = pointer to second FourCC
; outputs: Z set when all four bytes match, Z reset when any byte differs
; preserves: BC, DE, HL
; destroys: A
agnb_compare_fourcc:
    push bc
    push de
    push hl
    ld b,4
@loop:
    ld a,(de)
    cp (hl)
    jr nz,@done ; exit with Z reset if any byte differs, indicating a mismatch
    inc de
    inc hl
    djnz @loop ; if we fall throgh at the end of the loop Z is set, indicating a match
@done:
    pop hl
    pop de
    pop bc
    ret

; Open a container for reading.
; inputs:  DE = zero-terminated filename (normally agnb_filename)
; outputs: A=0 and Z set on success; A=agnb_error_open and NZ set on failure
;          agnb_fil initialized and agnb_file_is_open set on success
; destroys: AF, BC, HL
agnb_open:
; begin fail-closed: do not leave stale success state if ffs_fopen fails
    xor a
    ld (agnb_file_is_open),a
    ld (agnb_last_error),a

; open the caller-supplied filename into our single reader-owned FIL
    ld hl,agnb_fil
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    jr nz,@error

; ffs_fopen succeeded
    ld a,1
    ld (agnb_file_is_open),a
    xor a
    ret

@error:
    ld a,agnb_error_open
    ld (agnb_last_error),a
    or a
    ret

; Close agnb_fil if open and clear agnb_file_is_open.
; outputs: A=0 and Z set if closed or already closed
;          nonzero FatFS result and NZ set if ffs_fclose fails
; destroys: HL
agnb_close:
; An unopened file is already in the requested state.
    ld a,(agnb_file_is_open)
    or a
    jr z,@success

; Close our single reader-owned FIL.
    ld hl,agnb_fil
    FFSCALL ffs_fclose
    or a
    jr nz,agnb_error_close

; Only clear the open flag after FatFS confirms the close.
    xor a
    ld (agnb_file_is_open),a
@success:
    xor a
    ld (agnb_last_error),a
    ret

agnb_error_close:
; Placeholder in case we determine that close failures need a dedicated AGNB
; error code or recovery path. For now retain and return the nonzero FRESULT,
; and leave agnb_file_is_open set because FatFS did not confirm the close.
    ld (agnb_last_error),a
    or a
    ret

; Top-level image load operation.
; inputs:  none; uses agnb_filename
; outputs: all valid LIST BUFR image records uploaded to their explicit IDs
agnb_load_images:
    jp agnb_not_implemented

; Read exactly BC bytes from agnb_fil into DE.
; inputs:  BC = requested u24 length, DE = destination
; outputs: A=0 and Z set after the complete request is satisfied
;          nonzero error code and NZ set on FatFS error or premature EOF
;          state offset/count updated after every successful FatFS read
; destroys: BC, DE, HL
agnb_read_exact:
; A zero-length request is already complete.
    ld hl,0
    or a
    sbc hl,bc
    jr z,@success

@read:
; ffs_fread replaces BC with the number of bytes actually read, so retain the
; remaining request on the stack. It preserves DE, our current destination.
    push bc
    ld hl,agnb_fil
    FFSCALL ffs_fread
    or a
    jr nz,@fatfs_error

; Advance the u32 logical position by the returned u24 byte count.
    ld hl,(agnb_state+agnb_state_file_offset)
    add hl,bc
    ld (agnb_state+agnb_state_file_offset),hl
    ld a,(agnb_state+agnb_state_file_offset+3)
    adc a,0
    jr c,@offset_overflow
    ld (agnb_state+agnb_state_file_offset+3),a

; Retain the count returned by this individual FatFS read.
    ld (agnb_state+agnb_state_bytes_read),bc
    xor a
    ld (agnb_state+agnb_state_bytes_read+3),a

; Recover the remaining request and reject zero bytes as premature EOF.
    pop hl
    push hl
    ld hl,0
    or a
    sbc hl,bc
    pop hl
    jr z,@eof

; Subtract the returned count from the remaining request. FatFS must never
; report more bytes than were requested.
    or a
    sbc hl,bc
    jr c,@read_error

; Advance the destination by the returned byte count.
    ex de,hl
    add hl,bc
    ex de,hl

; Continue after a short read, or return once the request is satisfied.
    ld bc,0
    or a
    sbc hl,bc
    jr z,@success
    push hl
    pop bc
    jr @read

@fatfs_error:
    pop bc
@read_error:
    ld a,agnb_error_read
    jr @error
@offset_overflow:
    pop bc
    ld a,agnb_error_bounds
    jr @error
@eof:
    ld a,agnb_error_eof
@error:
    ld (agnb_last_error),a
    or a
    ret

@success:
    xor a
    ld (agnb_last_error),a
    ret

; Seek to a u32 absolute file offset.
; inputs:  C = most-significant byte, DE = low 24 bits
; outputs: agnb_state_file_offset updated on success
agnb_seek_absolute:
    jp agnb_not_implemented

; Read and validate RIFF size/form, establishing physical and RIFF bounds.
; inputs:  agnb_fil is open and positioned at byte zero
; outputs: A=0 and Z set on success; nonzero error code and NZ set on failure
;          file size and RIFF end stored in agnb_state
; destroys: BC, DE, HL
agnb_read_riff_header:
; retain the physical u32 file size recorded by FatFS in the FIL object
    ld hl,(agnb_fil+fil_obj+ffobjid_objsize)
    ld (agnb_state+agnb_state_file_size),hl
    ld a,(agnb_fil+fil_obj+ffobjid_objsize+3)
    ld (agnb_state+agnb_state_file_size+3),a

; read the complete fixed-size RIFF header before inspecting any field
    ld bc,agnb_riff_header_size
    ld de,agnb_header
    call agnb_read_exact
    ret nz

; validate the RIFF container identifier
    ld hl,agnb_header+agnb_riff_id
    ld de,agnb_id_riff
    call agnb_compare_fourcc
    jr nz,@bad_riff_id

; validate that this RIFF contains the AGNB form
    ld hl,agnb_header+agnb_riff_form
    ld de,agnb_id_agnb
    call agnb_compare_fourcc
    jr nz,@bad_riff_form

; RIFF stores file size minus eight. Add the omitted bytes as u32, using the
; native 24-bit ALU for the low three bytes and A for the high byte.
    ld hl,(agnb_header+agnb_riff_size)
    ld a,(agnb_header+agnb_riff_size+3)
    ld de,8
    add hl,de
    jr nc,@riff_end_ready
    inc a
    jr z,@bad_bounds             ; u32 addition overflowed
@riff_end_ready:
    ld (agnb_state+agnb_state_riff_end),hl
    ld (agnb_state+agnb_state_riff_end+3),a

; Version 0.1 requires RIFF size to equal the physical file size minus eight.
    ld de,(agnb_state+agnb_state_file_size)
    or a
    sbc hl,de
    jr nz,@bad_bounds
    ld a,(agnb_state+agnb_state_riff_end+3)
    ld hl,agnb_state+agnb_state_file_size+3
    cp (hl)
    jr nz,@bad_bounds

; valid RIFF/AGNB header
    xor a
    ld (agnb_last_error),a
    ret

@bad_riff_id:
    ld a,agnb_error_riff_id
    jr @error
@bad_riff_form:
    ld a,agnb_error_riff_form
    jr @error
@bad_bounds:
    ld a,agnb_error_bounds
@error:
    ld (agnb_last_error),a
    or a
    ret

; Read a generic eight-byte chunk header into agnb_header and compute its
; aligned payload end without crossing the active RIFF/LIST boundary.
agnb_read_chunk_header:
    jp agnb_not_implemented

; Validate the single VERS payload and supported version.
agnb_read_vers:
    jp agnb_not_implemented

; Parse one LIST BUFR and require BHDR, IMAG, DATA in that order.
agnb_read_buffer_list:
    jp agnb_not_implemented

; Read and validate BHDR into agnb_metadata.
agnb_read_bhdr:
    jp agnb_not_implemented

; Read and validate IMAG into agnb_metadata.
agnb_read_imag:
    jp agnb_not_implemented

; Validate DATA size after BHDR/IMAG, then stream it in filedata-sized blocks
; to agnb_meta_bufferId and consolidate/create the RGBA2222 bitmap.
agnb_stream_data:
    jp agnb_not_implemented

; Skip an unknown or deliberately ignored chunk, including alignment padding,
; without crossing the active enclosing boundary.
agnb_skip_chunk:
    jp agnb_not_implemented

; Round a u32 size or offset up to the next four-byte boundary.
; Calling convention will be finalized with the 32-bit arithmetic helper.
agnb_align4:
    jp agnb_not_implemented

; Common fail-closed body used by every scaffolded routine.
agnb_not_implemented:
    ld a,agnb_error_not_implemented
    ld (agnb_last_error),a
    or a ; return NZ
    ret
