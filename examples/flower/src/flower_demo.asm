    assume adl=1   
    org 0x040000    

    include "mos_api.inc"

    MACRO PROGNAME
    ASCIZ "flower_demo"
    ENDMACRO

    jp start       

_exec_name:
	PROGNAME

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

; APPLICATION INCLUDES
filedata: equ 0xB7E000 ; start address of 8k onboard sram
    include "basic/fpp.asm"
    include "functions.inc"
	include "maths.inc"
    include "mathfpp.inc"
    include "vdu.inc"
    include "parse_args.inc"

init:
; ========================================
; BASIC INITIALIZATION CODE FROM basic/init.asm
; ========================================
;
;Clear the application memory
;
_clear_ram:	
    push hl
    PUSH		BC
    LD		HL, RAM_START		
    LD		DE, RAM_START + 1
    LD		BC, RAM_END - RAM_START - 1
    XOR		A
    LD		(HL), A
    LDIR
    POP		BC
    pop hl

; initialization done
    RET

; ========================================
; MAIN PROGRAM
; ========================================
; ---- input arguments (float) ----
input_params_num: equ 8
input_params:
petals:             db   0x81, 0x1E, 0x85, 0xEB, 0x41 ; 3.03
vectors:            db   0x80, 0xD7, 0xA3, 0x70, 0x7D ; 1.98
depth:              db   0x7F, 0x99, 0x99, 0x99, 0x19 ; 0.6
periods:            db   0x86, 0x00, 0x00, 0x00, 0x04 ; 66
shrink:             db   0x7F, 0xCC, 0xCC, 0xCC, 0x4C ; 0.8
radius_scale: 	    db   0x88, 0x00, 0x00, 0x00, 0x00 ; 256
theta_init: 	    db   0x00, 0x00, 0x00, 0x00, 0x00 ; 0
loops: blkb 5,0 ; starts as float, but will be converted to int

target_params: blkb input_params_num*5,0

; ---- amount to increment each parameter each loop (float) ----
inc_params:
petals_inc: blkb 5,0
vectors_inc: blkb 5,0
depth_inc: blkb 5,0
periods_inc: blkb 5,0
shrink_inc: blkb 5,0
radius_scale_inc: blkb 5,0
theta_init_inc: blkb 5,0

G9: DW 9 ; format code for converting floats to strings

; ---- list of input arguments to cycle through ----
cur_sample: dl samples ; address of the current sample
next_sample: dl samples ; address of the next sample
samples:
    asciz "3 4 .5 30 1 320 0 10"
    asciz "3 4 .5 30 -320 1 0 10"

    asciz "4 5 .5 30 1 320 0 10"
    asciz "4 5 .5 30 -320 1 0 10"
    
    asciz "5 5 .5 30 1 320 0 10"
    asciz "5 5 .5 30 -320 1 0 10"

    asciz "6 5 .5 30 1 320 0 10"
    asciz "6 5 .5 30 -320 1 0 10"

    asciz "7 5.01 0.5 50 1 320 90 10"
    asciz "7 5.01 0.5 50 -320 1 90 10"

    asciz "3.03 1.98 .6 66 .8 320 90 10"
    asciz "3.03 1.98 .6 66 -320 .8 90 10"

    asciz "2.5 1.001 1 500 1 320 90 10"
    asciz "2.5 1.001 1 500 -320 1 90 10"

    dl 0 ; list terminator

main:
; set up the display
    ld a,18;+128 ; 146   1024  768   2     60hz  double-buffered
    call vdu_set_screen_mode

; set the cursor off
	call cursor_off

main_loop:
; prepare to read the parameter string
    ld de,command1
    ld hl,(cur_sample)    
    ld a,(hl)
    or a
    jp nz,@loop ; not at end of list so proceed
    ld hl,samples ;loop back to beginning of list
    ld (cur_sample),hl

@loop:
; copy the orginal string to the command buffer since _parse_params zero-terminates each token
    ld a,(hl)
    ld (de),a
    inc hl
    inc de
    or a
    jp nz,@loop
    ; inc hl            ; point to the next sample
    ld (next_sample),hl ; and store it

; parse the parameters
    ld hl,command1
    LD IX,argv_ptrs		; The argv array pointer address
    PUSH IX
    CALL _parse_params	; Parse the parameters
    POP IX

; convert the strings to floats and store them in the input_params table
    ld iy,input_params
    call load_input

; convert the loaded values back into strings and assemble the final command string
    ld b,input_params_num ; loop counter
    ld iy,input_params  ; point to the parameter values table
    ld ix,command1      ; point to the command string buffer
@loop0:
    push bc             ; save the loop counter
    push iy             ; save the parameter pointer
    push ix             ; save the command string pointer
    call fetch_float_iy_nor
    ld de,ACCS          ; point to the string accumulator
    ld ix,G9-1          ; get the format code for the number
    call STR_FP         ; convert the number to a string
    ex de,hl            ; point to end of the string
    ld (hl),0           ; null-terminate the string
    ld hl,ACCS          ; point to the string accumulator
    pop ix             ; get back the command string pointer
@loop1:
    ld a,(hl)           ; get a character
    ld (ix),a           ; store it
    inc hl              ; point to the next character
    lea ix,ix+1         ; point to the next character
    or a                ; check for end of string
    jr nz,@loop1        ; loop until done

    ld a,' '            ; overwrite the null with a space ...
    ld (ix-1),a         ; ... in case we're not at the end
    pop iy              ; get back the parameter pointer
    lea iy,iy+5         ; point to the next parameter
    pop bc              ; get back the loop counter
    djnz @loop0         ; loop until done

    xor a
    ld (ix),a           ; now null-terminate the command string

; draw the flower
    call draw_flower

; flip the screen
	call vdu_flip

; bump pointer to the next sample 
    ld hl,(next_sample)
    ld (cur_sample),hl

; check for escape key and quit if pressed
	MOSCALL mos_getkbmap
; 113 Escape
    bit 0,(ix+14)
	jr nz,main_end
@Escape:
	jp main_loop

main_end:
; restore screen to something normalish
    ld a,20 ; 20    512   384   64    60hz  single-buffered
	call vdu_set_screen_mode
	call cursor_on
	ret

; inputs: ix points to the start of the argument pointers
;         iy points to the start of the parameter values table
load_input:
    ld b,input_params_num ; loop counter
@loop:
    push bc ; save the loop counter
    call store_arg_iy_float ; get the next argument and store it
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

draw_flower:
    ld hl,command0
    MOSCALL mos_oscli
    ld a,' ' ; restore the space after "flower" since mos_oscli 
    ld (command1-1),a ; annoyingly null-terminates each argument
    ret

; @command: asciz "flower 3.93 1.98 .6 66 .8 320 90"
command0: db "flower " 
command1: blkb 256-7,0 

    include "basic/ram.asm" ; must be last so that RAM has room for BASIC operations