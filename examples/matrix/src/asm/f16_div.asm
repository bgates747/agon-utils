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
    ld hl,f16_fil
    ld de,test_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    jr z,@open_outfile
    call printInline
    asciz "Error opening file for reading\r\n"
; open file for writing
@open_outfile:
    ld hl,f16_fil_out
    ld de,test_filename_out
    ld c,fa_write | fa_open_existing
    FFSCALL ffs_fopen
    or a
    jr z,@read_loop
    call printInline
    asciz "Error opening file for writing\r\n"
    ret
@read_loop:
; read data from file
    ld hl,f16_fil
    ld de,filedata
    ld bc,480000 ; max bytes to read
    FFSCALL ffs_fread
    ld (bytes_read),bc
    push bc
    pop hl
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
    asciz " bytes read\r\n"
; start stopwatch
    call vdu_flip
    call stopwatch_set
; reset data pointer
    ld iy,filedata
@loop:
; perform division 
    ld l,(iy+0) ; op1 low byte
    ld h,(iy+1) ; op1 high byte
    ld e,(iy+2) ; op2 low byte
    ld d,(iy+3) ; op2 high byte
    call f16_div
; write results to file buffer
    ld (iy+6),l ; assembly quotient low byte
    ld (iy+7),h ; assembly quotient high byte
; check for error
    ld e,(iy+4) ; python quotient low byte
    ld d,(iy+5) ; python quotient high byte
    or a ; clear carry
    sbc.s hl,de
    jr z,@next_record
@error:
    ld hl,(errors)
    inc hl
    ld (errors),hl
@next_record:
    lea iy,iy+bytes_per_record ; bump data pointer
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
; ; DEBUG
;     push hl
;     call printDec
;     call printInline
;     asciz " ticks elapsed\r\n"
;     pop hl
; ; END DEBUG
    ld de,(time)
    add hl,de
    ld (time),hl
; write data to file
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,(bytes_read) ; bytes to write
    FFSCALL ffs_fwrite
    push bc
    pop hl
    call printDec
    call printInline
    asciz " bytes written\r\n"
; read next batch from file
    jp @read_loop
@read_end:
; close files
    ld hl,f16_fil
    FFSCALL ffs_fclose
    ld hl,f16_fil_out
    FFSCALL ffs_fclose
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
    ld hl,f16_fil
    ld de,test_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for reading\r\n"
    ret

open_outfile_write:
; open file for writing
    ld hl,f16_fil_out
    ld de,test_filename_out
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for writing\r\n"
    ret

open_outfile_write:
; open file for writing
    ld hl,f16_fil_out
    ld de,test_filename_out
    ld c,fa_write | fa_open_existing
    ; ld c,fa_write | fa_create_always
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for writing\r\n"
    ret

close_infile:
    ld hl,f16_fil
    FFSCALL ffs_fclose
    ret

close_outfile:
    ld hl,f16_fil_out
    FFSCALL ffs_fclose
    ret

test_filename: asciz "fp16_div_test.bin"
test_filename_out: asciz "fp16_div_test.bin"

    include "files.inc"
