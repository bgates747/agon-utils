; Routines selected from functions.inc
; Retained in original source-file order.

printString:
    PUSH BC
    LD BC,0
    LD A,0
    RST.LIL 18h
    POP BC
    RET
; print a VDU sequence
; HL: Pointer to VDU sequence - <1 byte length> <data>

printDec:
; BEGIN MY CODE
; back up all the things
    push af
    push bc
    push de
    push hl
; END MY CODE
    LD DE, _printDecBuffer
    CALL u24_to_ascii
; BEGIN MY CODE
; replace leading zeroes with spaces
    LD HL, _printDecBuffer
    ld B, 7 ; if HL was 0, we want to keep the final zero 
@loop:
    LD A, (HL)
    CP '0'
    JP NZ, @done
    LD A, ' '
    LD (HL), A
    INC HL
    ; CALL vdu_cursor_forward
    DJNZ @loop
@done:
; END MY CODE
    LD HL, _printDecBuffer
    CALL printString
; BEGIN MY CODE
; restore all the things
    pop hl
    pop de
    pop bc
    pop af
; END MY CODE
    RET
_printDecBuffer: blkb 16,0 ; a few bytes extra just to be sure

; This routine converts the unsigned 24-bit value in HLU into it's ASCII representation, 
; starting to memory location pointing by DE, in decimal form and with leading zeroes 
; so it will allways be 8 characters length
; HL : Value to convert to string
; DE : pointer to buffer, at least 8 byte + 0

u24_to_ascii:
    LD BC,-10000000
    CALL @one_digit
    LD BC,-1000000
    CALL @one_digit
    LD BC,-100000
    CALL @one_digit
    LD BC,-10000
    CALL @one_digit
    LD BC,-1000
    CALL @one_digit
    LD BC,-100
    CALL @one_digit
    LD C,-10
    CALL @one_digit
    LD C,B
@one_digit:
    LD A,'0'-1
@divide_me:
    INC A
    ADD HL,BC
    JR C,@divide_me
    SBC HL,BC
    LD (DE),A
    INC DE
    RET


; Routines, constants, and private data selected from vdu.inc
; Retained in original source-file order.

plot_bmp: equ 0xE8
dr_abs_fg: equ 5

cursor_on:
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:
	db 23,1,1
@end:

cursor_off:	
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:
	db 23,1,0
@end:

; VDU 9: Move cursor forward one character

vdu_move_cursor:
    ld (@x0),bc
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: 	db 31
@x0:	db 0
@y0: 	db 0
@end: 	db 0 ; padding

; VDU 12: Clear text area (CLS)

vdu_cls:
    ld a,12
	rst.lil $10  
	ret

vdu_set_screen_mode:
	ld (@arg),a        
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 22 ; set screen mode
@arg: db 0  ; screen mode parameter
@end:

; VDU 23, 0, &C0, n: Turn logical screen scaling on and off *
; inputs: a is scaling mode, 1=on, 0=off
; note: default setting on boot is scaling ON

vdu_set_scaling:
	ld (@arg),a        
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 23,0,0xC0
@arg: db 0  ; scaling on/off
@end: 

; VDU 23, 27, &20, bufferId; : Select bitmap (using a buffer ID)
; inputs: hl=bufferId

vdu_buff_select:
	ld (@bufferId),hl
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd: db 23,27,0x20
@bufferId: dw 0x0000
@end: db 0x00 ; padding

; VDU 23, 27, &21, w; h; format: Create bitmap from selected buffer
; inputs: a=format; bc=width; de=height
; prerequisites: buffer selected by vdu_bmp_select or vdu_buff_select
; formats: https://agonconsole8.github.io/agon-docs/VDP---Bitmaps-API.html
; 0 	RGBA8888 (4-bytes per pixel)
; 1 	RGBA2222 (1-bytes per pixel)
; 2 	Mono/Mask (1-bit per pixel)
; 3 	Reserved for internal use by VDP (“native” format)

vdu_bmp_create:
    ld (@width),bc
    ld (@height),de
    ld (@fmt),a
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:       db 23,27,0x21
@width:     dw 0x0000
@height:    dw 0x0000
@fmt:       db 0x00
@end:

; https://agonconsole8.github.io/agon-docs/VDP---PLOT-Commands.html
; &E8-&EF 	232-239 	Bitmap plot §
; VDU 25, mode, x; y;: PLOT command
; inputs: bc=x0, de=y0
; prerequisites: vdu_buff_select

vdu_plot_bmp:
    ld (@x0),bc
    ld (@y0),de
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:   db 25
@mode:  db plot_bmp+dr_abs_fg ; 0xED
@x0: 	dw 0x0000
@y0: 	dw 0x0000
@end:   db 0x00 ; padding

; scratch variables 
bufferId0: dl 0x000000
bufferId1: dl 0x000000

; load a vdu buffer from local memory
; inputs: hl = bufferId ; bc = length ; de = pointer to data

vdu_load_buffer:
    ld (@length),bc
    push de ; save data pointer
; send the vdu command string
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
; send the buffer data
    pop hl ; pointer to data
    ld bc,(@length)
    rst.lil $18 ; send it
    ret
; Upload data :: VDU 23, 0 &A0, bufferId; 0, length; <buffer-data>
@cmd:       db 23,0,0xA0
@bufferId:	dw 0x0000
		    db 0 ; load buffer
@length:	dw 0x0000
@end: db 0 ; padding

; clear a buffer
; inputs: hl = bufferId

vdu_clear_buffer:
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:       db 23,0,0xA0
@bufferId:	dw 0x0000
		    db 2 ; clear buffer
@end:

; Command 14: Consolidate blocks in a buffer

vdu_consolidate_buffer:
; set parameters for vdu call
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@beg
    ld bc,@end-@beg
    rst.lil $18
    ret
; VDU 23, 0, &A0, bufferId; 14
@beg: db 23,0,0xA0
@bufferId: dw 0x0000
           db 14
@end:

; load an image file to a buffer and make it a bitmap
; inputs: a = image type ; bc,de image width,height ; hl = bufferId ; ix = file size ; iy = pointer to filename

vdu_load_img:
; back up image type and dimension parameters
    ld (bufferId0),hl
    push af
	push bc
	push de
; load the image
	call vdu_load_buffer_from_file
; now make it a bitmap
    ld hl,(bufferId0)
    call vdu_consolidate_buffer
    ld hl,(bufferId0)
    call vdu_buff_select
	pop de ; image height
	pop bc ; image width
	pop af ; image type
	jp vdu_bmp_create ; will return to caller from there

; inputs: hl = bufferId; iy = pointer to filename

vdu_load_buffer_from_file:
    ld (bufferId0),hl

; clear target buffer
    call vdu_clear_buffer

; open the file in read mode
; Open a file
; HLU: Filename
;   C: Mode
; Returns:
;   A: Filehandle, or 0 if couldn't open
	push iy ; pointer to filename
	pop hl
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
    ld hl,filedata
    ld de,8192 ; max we can read into onboard sram at one time
    MOSCALL mos_fread

; test de for zero bytes read
    ld hl,0
    xor a ; clear carry
    sbc hl,de
    jp z,@close_file

; load a vdu buffer from local memory
; inputs: hl = bufferId ; bc = length ; de = pointer to data
    ld hl,(bufferId0)
    push de ; chunksize
    pop bc
    ld de,filedata
    call vdu_load_buffer

; ; print progress breadcrumbs
;     ld a,'.'
;     rst.lil 10h

; read the next block
    jp @read_file

; close the file
@close_file:
    ld a,(@filehandle)
    MOSCALL mos_fclose
    ret ; vdu_load_buffer_from_file

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
