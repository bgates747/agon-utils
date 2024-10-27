  			.ASSUME	ADL = 1			
			INCLUDE "mos_api.inc"
			ORG $b0000 ; Is a moslet
	
			MACRO PROGNAME
			ASCIZ "fontld.bin"
			ENDMACRO
			
  			include "init.inc"
			include "parse.inc"

; API includes
    include "functions.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_fonts.inc"

; Application includes
    include "fonts_list.inc"

; Main routine
_main:
    ld ix,font_list ; pointer to font list lookup
    ld b,num_fonts ; loop counter

@load_loop:
    push bc ; save loop counter

; load font into a buffer
; inputs: hl = bufferId; iy = pointer to filename
; VDU 23, 0, &95, 1, bufferId; filename: Load font from file
    ld hl,(ix+font_list_bufferId)
    ld iy,(ix+font_list_filename)
    call vdu_load_buffer_from_file

; create font from buffer
; inputs: hl = bufferId, e = width, d = height, d = ascent, a = flags
; VDU 23, 0, &95, 1, bufferId; width, height, ascent, flags: Create font from buffer
    ld hl,(ix+font_list_bufferId)
    ld a,(ix+font_list_width)
    ld e,a  ; width
    ld a,(ix+font_list_height)
    ld d,a  ; height and ascent
    ld a,0 ; flags
    call vdu_font_create

; select font
; inputs: hl = bufferId, a = font flags
; VDU 23, 0, &95, 0, bufferId; flags: Select font
; Flags:
; Bit	Description
; 0	Adjust cursor position to ensure text baseline is aligned
;   0: Do not adjust cursor position (best for changing font on a new line)
;   1: Adjust cursor position (best for changing font in the middle of a line)
; 1-7	Reserved for future use
    ld hl,(ix+font_list_bufferId)
    ld a,1 ; flags
    call vdu_font_select

; debug print filename
    call printNewLine
    ld hl,(ix+font_list_filename)
    call printString

; advance font_list pointer to next record
    lea ix,ix+font_list_record_size

; restore loop counter
    pop bc
    djnz @load_loop

    call printNewLine

main_end:		; End with no error
			LD 	HL, 0
			RET