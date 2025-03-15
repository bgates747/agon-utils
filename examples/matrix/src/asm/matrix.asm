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

; --- MACROS ---
	MACRO	MOSCALL	function
			LD	A, function
			RST.LIL	08h
	ENDMACRO 	

; --- CONSTANTS ---
c_blue_dk: equ 4
c_white: equ 15
filedata: equ 0xB7E000 ; address of onboard 8k sram
mos_sysvars:		EQU	08h
fa_read:			EQU	01h
mos_fopen:			EQU	0Ah
mos_fread:			EQU	1Ah
mos_fclose:			EQU	0Bh
fn_img: asciz "ctl_panel_navball.rgba2"

; --- VARIABLES ---
img_width: equ 79
img_height: equ 79
buff_img: equ 256
buff_xform: equ 257
buff_img_xform: equ 258
rotation: dw32 0 ; rotation to apply (can be degrees or radians, 16 or 32 bit, fixed or floating point, depending on options)


; --- MAIN PROGRAM FILE ---
init:
; clear all buffers
    call vdu_clear_all_buffers
; set up the display
    ld a,8+128 ; 320x240x64 60Hz double-buffered
    call vdu_set_screen_mode
    xor a
    call vdu_set_scaling
; set text background color
    ld a,c_blue_dk+128
    call vdu_colour_text
; set text foreground color
    ld a,c_white
    call vdu_colour_text
    call vdu_cls
; set the cursor off
    call vdu_cursor_off
    ret

; end init
main:
; load a test bitmap
    ld a,1 ; type rgba2222
    ld hl,buff_img ; bufferId
    ld bc,img_width ; width
    ld de,img_height ; height
    ld iy,fn_img ; filename
    call vdu_load_img

; enable transform matrices
    call vdu_enable_transforms

    ; ld hl,1        ; anticlockwise degrees 360 in 16.0 fixed-point
    ; ld hl,0x2478 ; 1 degree converted to radians in 16-bit floating point
    ld hl,0x2478+0x8000 ; -1 degree converted to radians in 16-bit floating point
    ld (rotation),hl
@loop:
; create a rotation transform matrix
    ; ld a,2 ; anticlockwise rotation in degrees
    ; ld ixl,$80 | $40 | 0 ; 16-bit | fixed-point | 0 shift = 16.0 fixed-point

    ld a,3 ; anticlockwise rotation in radians
    ld ixl,$80 | $00 | 0 ; 16-bit | floating-point | 0 shift

    ld bc,2 ; argument length: 2 bytes to a 16.0 fixed-point number

    ld de,rotation ; argument pointer
    ld hl,buff_xform ; matrix bufferId
    call vdu_do_2d_matrix_transform

; apply transform matrix to bitmap
    xor a ; clear options
    ; set 1,a ; automatically resize bitmap
    ; set 2,a ; resize bitmap to specified dimensions
    ; ld ix,24 ; x size
    ; ld iy,24 ; y size
    ; set 4,a ; automatically translate target bitmap position
    ld hl,buff_img ; source bitmap bufferId
    ld de,buff_img_xform ; destination bufferId
    ld bc,buff_xform ; transform matrix bufferId
    call vdu_transform_bitmap

; plot the transformed bitmap
    ; ld a,%00100000
    ; call multiPurposeDelay
    call vdu_cls
    ld hl,buff_img_xform
    call vdu_buff_select
    ld bc,128 ; x
    ld de,64 ; y
    call vdu_plot_bmp
    call vdu_flip

; ; plot the raw bitmap
;     ld hl,buff_img
;     call vdu_buff_select
;     ld bc,0 ; x
;     ld de,8 ; y
;     call vdu_plot_bmp

    jr @loop

    ret ; back to MOS
; end main

; ----- MAIN MATRIX TRANSFORM FUNCTIONS -----

; Command 23: Set affine transforms test flag
; VDU 23, 0, &F8, 1; 1;
; inputs: none
vdu_enable_transforms:
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:   db 23,0,0xF8
        dw 1 ; magic number
        dw 1 ; ditto
@end:
; end vdu_enable_transforms

; Command 32: Create or manipulate a 2D affine transformation matrix
; VDU 23, 0, &A0, bufferId; 32, operation, [<format>, <arguments...>] 
; inputs: a = operation, hl = bufferId, de = pointer to arguments, bc = length of arguments, ixl = format
vdu_do_2d_matrix_transform:
    push af ; save operation
    push bc ; length of arguments
    push de ; pointer to arguments
    ld (@operation),a
    ld a,l
    ld (@bufferId+0),a
    ld a,h
    ld (@bufferId+1),a
    ld a,ixl
    ld (@format),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop hl ; pointer to arguments (was de)
    pop bc ; length of arguments
    pop af ; restore operation
    cp 1 ; if > 1, send the arguments
    ret c ; no arguments
    rst.lil $18 ; send the arguments
    ret
@cmd:       db 23,0,0xA0
@bufferId:  dw 0x0000
            db 32 ; create transform matrix
@operation: db 0x00
@format:    db 0x00
@end:
; end vdu_do_2d_matrix_transform

; Command 40: Create a transformed bitmap
; VDU 23, 0, &A0, bufferId; 40, options, transformBufferId; sourceBitmapId; [width; height;]
; inputs a = options, de = bufferId, bc = transformBufferId, hl = sourceBitmapId, ix = width, iy = height
; options:
; Bit value Arguments       Description
; 1 		                Target bitmap should be resized. When not set, target will be same dimensions as the original bitmap.
; 2 	    width; height; 	Target bitmap will be resized to explicitly given dimensions
; 4 Automatically translate target bitmap position. When set the calculated transformed minimum x,y coordinates will be placed at the top left of the target
vdu_transform_bitmap:
    push af ; save options
    ld (@options),a
    ld a,e
    ld (@bufferId+0),a
    ld a,d
    ld (@bufferId+1),a
    ld (@transformBufferId),bc
    ld (@sourceBitmapId),hl
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop af ; restore options
    bit 2,a ; check resize bit
    ret z
    ld (@width),ix
    ld (@height),iy
    ld hl,@width
    ld bc,4
    rst.lil $18
    ret
@cmd:       db 23,0,0xA0
@bufferId:  dw 0x0000
            db 40 ; create transformed bitmap
@options:   db 0x00
@transformBufferId: dw 0x0000
@sourceBitmapId:    dw 0x0000
@end:       db 0x00 ; padding
; these are only included when bit 2 of options (resize) is set
@width:     dw 0x0000
@height:    dw 0x0000
            db 0x00 ; padding
; end vdu_transform_bitmap

; ----- HELPER FUNCTIONS -----
; Command 2: Clear a buffer
; VDU 23, 0 &A0, bufferId; 2
; inputs: hl = bufferId
vdu_clear_buffer:
    ld (@bufferId),hl
    ld a,2 ; clear buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 2 ; clear buffer
@end: 
; end vdu_clear_buffer

vdu_clear_all_buffers:
; clear all buffers
    ld hl,@beg
    ld bc,@end-@beg
    rst.lil $18
    ret
@beg: db 23,0,$A0
      dw -1 ; bufferId -1 (65535) means clear all buffers
      db 2  ; command 2: clear a buffer
@end:
; end vdu_clear_all_buffers

vdu_set_screen_mode:
	ld (@arg),a        
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 22 ; set screen mode
@arg: db 0  ; screen mode parameter
@end:

vdu_set_scaling:
	ld (@arg),a        
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 23,0,0xC0
@arg: db 0  ; scaling on/off
@end: 

; VDU 17, colour: Define text colour (COLOUR)
vdu_colour_text:
	ld (@arg),a        
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 17
@arg: db 0 
@end:
vdu_cls:
    ld a,12
	rst.lil $10  
	ret

vdu_cursor_off:	
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:
	db 23,1,0
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

vdu_flip:       
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 23,0,0xC3
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


; 5 	Plot absolute in current foreground colour
dr_abs_fg: equ 5
plot_bmp: equ 0xE8

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


; scratch variables 
bufferId0: dl 0x000000
bufferId1: dl 0x000000

; load an image file to a buffer and make it a bitmap
; inputs: a = image format ; bc,de image width,height ; hl = bufferId ; iy = pointer to filename
; formats: https://agonconsole8.github.io/agon-docs/VDP---Bitmaps-API.html
; 0 	RGBA8888 (4-bytes per pixel)
; 1 	RGBA2222 (1-bytes per pixel)
; 2 	Mono/Mask (1-bit per pixel)
; 3 	Reserved for internal use by VDP (“native” format)
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

