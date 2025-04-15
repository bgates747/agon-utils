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
        call printInline
        asciz "\r\n",msg,"\r\n"
        pop hl
        push hl
        call printHLHexBin
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

main:
    ; call printInline
    ; asciz "\r\nTest me:\r\n"
    ; call test_me
    ; call printNewLine

    call printInline
    asciz "\r\nTest Xeda:\r\n"
    call test_xeda
    call printNewLine

    ; call printInline
    ; asciz "\r\nTest Calc84Maniac:\r\n"
    ; call test_calc84maniac
    ; call printNewLine

    ret

test_xeda:
; set up counters
    ld hl,0 ; error counter
    ld (errors),hl ; error counter
    ld (records),hl ; record counter
    ld (time),hl ; time counter
; open file for reading
    ld hl,f16_fil
    ld de,mul_test_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    jr z,@open_outfile
    call printInline
    asciz "Error opening file for reading\r\n"
; open file for writing
@open_outfile:
    ld hl,f16_fil_out
    ld de,mul_test_filename_out
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
    ld bc,480000 ; bytes to read
    FFSCALL ffs_fread
    ld (bytes_read),bc
    push bc
    pop hl
    SIGN_HLU
    jp z,@read_end
; compute number of records in batch
    push hl
    ld de,12 ; bytes per record
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
    ld e,(ix+0) ; op1 low byte
    ld d,(ix+1) ; op1 high byte
    ld c,(ix+2) ; op2 low byte
    ld b,(ix+3) ; op2 high byte
    call div_16_xeda
; write results to file buffer
    ld (ix+8),e ; assembly quotient low byte
    ld (ix+9),d ; assembly quotient high byte
    ld (ix+10),l ; assembly remainder low byte
    ld (ix+11),h ; assembly remainder high byte
; check for error
    ld l,(ix+8) ; assembly quotient low byte
    ld h,(ix+9) ; assembly quotient high byte
    ld e,(ix+4) ; python quotient low byte
    ld d,(ix+5) ; python quotient high byte
    or a ; clear carry
    sbc.s hl,de
    jr nz,@error
    ld l,(ix+10) ; assembly remainder low byte
    ld h,(ix+11) ; assembly remainder high byte
    ld e,(ix+6) ; python remainder low byte
    ld d,(ix+7) ; python remainder high byte
    or a ; clear carry
    sbc.s hl,de
    jr nz,@error
    jr @next_record
@error:
    ld hl,(errors)
    inc hl
    ld (errors),hl
@next_record:
    lea ix,ix+12 ; bump data pointer
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
; DEBUG
    push hl
    call printDec
    call printInline
    asciz " ticks elapsed\r\n"
    pop hl
; END DEBUG
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

mul_test_filename: asciz "div_16_test.bin"
mul_test_filename_out: asciz "div_16_test.bin"

    include "files.inc"
