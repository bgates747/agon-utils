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

main:

; FAILS 7C00
    call printInline
    asciz "0.0 / 0.0 = nan\r\n"
    call printInline
    asciz "0x0000 / 0x0000 = 0xFE00\r\n"
    ld de,0x0000 ; 0.0
    ld bc,0x0000 ; 0.0
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; FAILS 77FF
    call printInline
    asciz "1.0 / 0.0 = inf\r\n"
    call printInline
    asciz "0x3C00 / 0x0000 = 0x7C00\r\n"
    ld de,0x3C00 ; 1.0
    ld bc,0x0000 ; 0.0
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; FAILS 17FF
    call printInline
    asciz "5.9604645e-08 / 0.0 = inf\r\n"
    call printInline
    asciz "0x0001 / 0x0000 = 0x7C00\r\n"
    ld de,0x0001 ; 5.9604645e-08
    ld bc,0x0000 ; 0.0
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; PASSES 
    call printInline
    asciz "inf / 0.0 = nan\r\n"
    call printInline
    asciz "0x7C00 / 0x0000 = 0xFE00\r\n"
    ld de,0x7C00 ; inf
    ld bc,0x0000 ; 0.0
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; PASSES
    call printInline
    asciz "nan / 0.0 = nan\r\n"
    call printInline
    asciz "0x7E00 / 0x0000 = 0xFE00\r\n"
    ld de,0x7E00 ; nan
    ld bc,0x0000 ; 0.0
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; PASSES
    call printInline
    asciz "1.0 / 5.9604645e-08 = inf\r\n"
    call printInline
    asciz "0x3C00 / 0x0001 = 0x7C00\r\n"
    ld de,0x3C00 ; 1.0
    ld bc,0x0001 ; 5.9604645e-08
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

; FAILS FE00
    call printInline
    asciz "inf / 5.9604645e-08 = inf\r\n"
    call printInline
    asciz "0x7C00 / 0x0001 = 0x7C00\r\n"
    ld de,0x7C00 ; inf
    ld bc,0x0001 ; 5.9604645e-08
    call f16_div
    PRINT_HL_HEX " assembly result"
    call printNewLine

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
    call div_16_32_xeda
; write results to file buffer
    ld (ix+8),e ; assembly integer low byte
    ld (ix+9),d ; assembly integer high byte
    ld (ix+10),l ; assembly fraction low byte
    ld (ix+11),h ; assembly fraction high byte
; check for error
    ld l,(ix+8) ; assembly integer low byte
    ld h,(ix+9) ; assembly integer high byte
    ld e,(ix+4) ; python integer low byte
    ld d,(ix+5) ; python integer high byte
    or a ; clear carry
    sbc.s hl,de
    jr nz,@error
    ld l,(ix+10) ; assembly fraction low byte
    ld h,(ix+11) ; assembly fraction high byte
    ld e,(ix+6) ; python fraction low byte
    ld d,(ix+7) ; python fraction high byte
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

mul_test_filename: asciz "div_16_32_test.bin"
mul_test_filename_out: asciz "div_16_32_test.bin"

    include "files.inc"
