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

    MACRO PRINT_UNPACK_F16 msg
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        call printUnpackF16
    ENDMACRO

    MACRO PRINT_PACK_F16 msg
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        call printPackF16
    ENDMACRO

    MACRO PRINT_HL_HEX_BIN msg
        push de
        push af
        push hl
        call printHLHexBin
        pop hl
        push hl
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_A_HEX msg
        push de
        push hl
        push af
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        pop af
        push af
        call printHexA
        call printInline
        asciz "  ",msg,"\r\n"
        pop af
        pop hl
        pop de
    ENDMACRO

    MACRO PRINT_HL_HEX msg
        push de
        push af
        push hl
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        call printHexHL
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_UHL_HEX msg
        push de
        push af
        push hl
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        call printHexUHL
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_AUHL_HEX msg
        push de
        push af
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        pop af
        call printHexAUHL
        call printInline
        asciz msg,"\r\n"
        pop de
    ENDMACRO

    MACRO PRINT_BC_HEX msg
        push de
        push af
        push hl
        push bc
        pop hl
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        call printHexHL
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_DE_HEX msg
        push de
        push af
        push hl
        ex de,hl
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        call printHexHL
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_HLDE_HEX msg
        push de
        push af
        push hl
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        call printHexHLDE
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO PRINT_AHL_HEX msg
        push de
        push af
        push hl
        push af
        ld a,'0'
        rst.lil 0x10
        ld a,'x'
        rst.lil 0x10
        pop af
        call printHexAHL
        call printInline
        asciz msg,"\r\n"
        pop hl
        pop af
        pop de
    ENDMACRO

    MACRO DUMP_REGISTERS_HEX msg
        push de
        push af
        push hl
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        pop af
        pop de
        call dumpRegistersHex
        ; call dumpFlags
    ENDMACRO

printHLHexBin:
    call printHexHL
    call printBinHL
    ret


; API INCLUDES
    include "mos_api.inc"
    include "macros.inc"
    include "functions.inc"
    include "arith24.inc"
    include "fixed168.inc"
    include "maths.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_buffered_api.inc"
    include "vdu_plot.inc"

; APPLICATION INCLUDES
    include "softfloat/f16_mul.inc"
    include "softfloat/f16_div.inc"
    include "softfloat/internals.inc"
    include "softfloat/s_normSubnormalF16Sig.inc"
    include "softfloat/s_roundPackToF16.inc"
    include "softfloat/s_shiftRightJam32.inc"
    include "debug.inc"

errors: dl 0
records: dl 0
counter: dl 0
time: dl 0
bytes_read: dl 0
bytes_per_record: equ 8

main:
    ; call printInline
    ; asciz "7364.0 / -9752.0 = -0.75537109375\r\n"
    ; call printInline
    ; asciz "0x6F31 / 0xF0C3 = 0xBA0B\r\n"
    ; ld hl,0x6F31 ; 7364.0
    ; ld de,0xF0C3 ; -9752.0
    ; call f16_div
    ; PRINT_HL_HEX " assembly result"
    ; call printNewLine

    ; ret

test_fp16_div:
    call vdu_cls
    call printInline
    asciz "\r\nFP16 DIVISION TEST\r\n"
; set up counters
    ld hl,0 ; error counter
    ld (errors),hl ; error counter
    ld (records),hl ; record counter
    ld (time),hl ; time counter
; open file for reading
    call open_infile_read
    or a
    jr nz,@open_outfile
    call printInline
    asciz "Error opening file for reading\r\n"
    ret
@open_outfile:
; open file for writing
    call open_outfile_write
    or a
    jr nz,@read_loop
    call printInline
    asciz "Error opening file for writing\r\n"
    ret
@read_loop:
; read data from file
    ld a,(f16_file_in_handle)
    ld c,a
    ld hl,filedata
    ld de,480000 ; max bytes to read
    MOSCALL mos_fread
    ld (bytes_read),de
    ex de,hl
    SIGN_HLU
    jp z,@read_end
; compute number of records in batch
    push hl
    ld de,bytes_per_record ; bytes per record
    call udiv24
    ld (counter),de ; record counter
    ex de,hl
    call printDec
    call printInline
    asciz " records in batch"
    pop hl
; output bytes read
    call printDec
    call printInline
    asciz " bytes read"
; start stopwatch
    call vdu_flip
    call stopwatch_set
; reset data pointer
    ld ix,filedata
@loop:
; perform division 
    ld l,(ix+0) ; op1 low byte
    ld h,(ix+1) ; op1 high byte
    ld e,(ix+2) ; op2 low byte
    ld d,(ix+3) ; op2 high byte
    call f16_div
; write results to file buffer
    ld (ix+6),l ; assembly quotient low byte
    ld (ix+7),h ; assembly quotient high byte
; check for error
    ld e,(ix+4) ; python quotient low byte
    ld d,(ix+5) ; python quotient high byte
    or a ; clear carry
    sbc.s hl,de
    jr z,@next_record
@error:
    ld hl,(errors)
    inc hl
    ld (errors),hl
@next_record:
    lea ix,ix+bytes_per_record ; bump data pointer
    ld hl,(records)
    inc hl
    ld (records),hl
    ld hl,(counter)
    dec hl
    ld (counter),hl
    SIGN_HLU
    jr nz,@loop
; get elapsed time
    call stopwatch_get
    ld de,(time)
    add hl,de
    ld (time),hl
; write data to file
    ld a,(f16_file_out_write_handle)
    ld c,a
    ld hl,filedata
    ld de,(bytes_read) ; bytes to write
    MOSCALL mos_fwrite
    ex de,hl
    call printDec
    call printInline
    asciz " bytes written\r\n"
; read next batch from file
    jp @read_loop
@read_end:
; close files
    call close_infile
    call close_outfile_write
; report elapsed time
    ld hl,(time)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,120*256 ; ticks per second in 16.8 fixed point
    call udiv168
    call print_s168_de
    call printInline
    asciz " seconds elapsed\r\n"
; display error count
    ld hl,(errors)
    call printDec
    call printInline
    asciz " errors\r\n"
; display record count
    ld hl,(records)
    call printDec
    call printInline
    asciz " records\r\n"
    ret

open_infile_read:
; open file for reading
    ld hl,test_filename
    ld c,fa_read
    MOSCALL mos_fopen
    ld (f16_file_in_handle),a
    ret

open_outfile_read:
; open file for reading
    ld hl,test_filename_out
    ld c,fa_read
    MOSCALL mos_fopen
    ld (f16_file_out_read_handle),a
    ret

open_outfile_write:
; open file for writing
    ld hl,test_filename_out
    ld c,fa_write | fa_open_existing
    ; ld c,fa_write | fa_create_always
    MOSCALL mos_fopen
    ld (f16_file_out_write_handle),a
    ret

close_infile:
    ld a,(f16_file_in_handle)
    MOSCALL mos_fclose
    ret

close_outfile_read:
    ld a,(f16_file_out_read_handle)
    MOSCALL mos_fclose
    ret

close_outfile_write:
    ld a,(f16_file_out_write_handle)
    MOSCALL mos_fclose
    ret

f16_file_in_handle: db 0
f16_file_out_read_handle: db 0
f16_file_out_write_handle: db 0
test_filename: asciz "fp16_div_test.bin"
test_filename_out: asciz "fp16_div_test.bin"

    include "files.inc"
