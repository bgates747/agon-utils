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
    db "MOS", 00h, 01h 
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

; ---- list of input arguments to cycle through ----
cur_sample: dl samples ; address of the current sample
next_sample: dl samples ; address of the next sample
samples:
    asciz "3, 1.03703704, 0.5, 64, 1, 512, 90, 100"
    asciz "2.99, 0.96618358, 0.5, 64, 1, 512, 90, 1"

    ; asciz "3.03, 1.98019802, 0.0, 66, 1, 512, 90, 12"
    ; asciz "3.03, 1.98019802, 1.0, 66, 1, 512, 90, 1"

    ; asciz "6.96, 2.0028733, 0.4, 50, 1, 512, 90, 50"
    ; asciz "6.96, 2.01, 0.4, 50, 1, 512, 90, 1"

    ; asciz "6.99, 1.78826896, 0.5, 100, 0, 512, 90, 20"
    ; asciz "6.99, 1.81211254, 0.5, 100, 0, 512, 90, 1"

    ; asciz "6.966, 2.01, 0.4, 50, 1, 512, 90, 17"
    ; asciz "7.034, 2.00, 0.4, 50, 1, 512, 90, 1"
    ; asciz "6.966, 1.99, 0.4, 50, 1, 512, 90, 17"
    ; asciz "7.034, 2.00, 0.4, 50, 1, 512, 90, 17"

    dl 0; list terminator

; APPLICATION INCLUDES
filedata: equ 0xB7E000 ; start address of 8k onboard sram
    include "basic/fpp.asm"
    include "functions.inc"
	include "maths.inc"
    include "fpp_ext.inc"
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
petals:             db   0x81, 0x1F, 0x85, 0xEB, 0x41 ; 3.03
vectors:            db   0x80, 0xD7, 0xA3, 0x70, 0x7D ; 1.98
depth:              db   0x7F, 0x9A, 0x99, 0x99, 0x19 ; 0.6
periods:            db   0x00, 0x42, 0x00, 0x00, 0x00 ; 66.0
shrink:             db   0x7F, 0xCC, 0xCC, 0xCC, 0x4C ; 0.8
radius_scale: 	    db   0x00, 0x00, 0x02, 0x00, 0x00 ; 512.0
theta_init: 	    db   0x00, 0x00, 0x00, 0x00, 0x00 ; 0
num_increments:     db   0x00, 0x01, 0x00, 0x00, 0x00 ; 1.0

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

main:
; set up the display
    ld a,18+128 ; 18   1024  768   2     60hz  double-buffered
    call vdu_set_screen_mode
	call cursor_off

main_loop:
; get the starting parameters
    call get_params
    ld iy,input_params
    call load_input

; bump pointer to the next sample 
    ld hl,(next_sample)
    ld (cur_sample),hl 

; get the target parameters
    call get_params
    ld iy,target_params
    call load_input

; compute the increment parameters
    call compute_increments

; iterate to the target sample
    ld ix,target_params-5 ; point to num_increments
    call fetch_float_nor
    call int2hlu
    ld b,l ; loop counter

@loop:
    push bc
; assemble the command string and draw the flower
    call assemble_command
    call draw_flower
    call vdu_flip

    ; call waitKeypress
    call apply_increments

; check for escape key and quit if pressed
    MOSCALL mos_getkbmap
    pop bc ; get back the loop counter
; 113 Escape
    bit 0,(ix+14)
    jr nz,main_end
@Escape:
    djnz @loop ; loop until done

    jp main_loop

main_end:
; restore screen to something normalish
    ld a,20 ; 20    512   384   64    60hz  single-buffered
	call vdu_set_screen_mode
	call cursor_on
	ret

draw_flower:
    ld hl,command0
    MOSCALL mos_oscli
    ld a,' '          ; restore the space after "flower" since  
    ld (command1-1),a ; mos_oscli null-terminates each argument
    ret

get_params:
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
    ld (next_sample),hl
; parse the parameters
    ld hl,command1
    LD IX,argv_ptrs		; The argv array pointer address
    PUSH IX
    CALL _parse_params	; Parse the parameters
    POP IX
    ret

; inputs: ix points to the start of the argument pointers
;         iy points to the start of the parameter values table
; outputs: the parameter values are loaded into the table
;          hl points to the next parameter set
load_input:
    ld b,input_params_num ; loop counter
@loop:
    push bc ; save the loop counter
    call store_arg_iy_float ; get the next argument and store it
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

assemble_command:
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

    ret

offset_targets: equ input_params_num*5
offset_increments: equ input_params_num*5*2

compute_increments:
    ld b,input_params_num-1 ; loop counter (skip number of increments)
    ld iy,input_params  ; point to the parameter values table
@loop:
    push bc ; save the loop counter
    call fetch_float_targets_nor
    call fetch_float_iy_alt ; input_params
    ld a,fsub
    call FPP ; HLH'L'C = target - input
    ld ix,target_params-5 ; point to num_increments
    call fetch_float_alt
    ld a,fdiv
    call FPP ; HLH'L'C = (target - input) / num_increments
    call store_float_increments_nor
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

apply_increments:
    ld b,input_params_num ; loop counter
    ld iy,input_params  ; point to the parameter values table
@loop:
    push bc ; save the loop counter
    call fetch_float_iy_nor
    call fetch_float_increments_alt
    ld a,fadd
    call FPP ; HLH'L'C = input + increment
    call store_float_iy_nor
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

; fetch HLH'L'C floating point number from a 40-bit buffer
; inputs: iy = buffer address
; outputs: HLH'L'C = floating point number
; destroys: HLH'L'C
fetch_float_targets_nor:
    ld c,(iy+0+offset_targets)
    ld l,(iy+3+offset_targets)
    ld h,(iy+4+offset_targets)
    exx
    ld l,(iy+1+offset_targets)
    ld h,(iy+2+offset_targets)
    exx
    ret

; store HLH'L'C floating point number in a 40-bit buffer
; inputs: HLH'L'C = floating point number
;         iy = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_increments_nor:
    ld (iy+0+offset_increments),c
    ld (iy+3+offset_increments),l
    ld (iy+4+offset_increments),h
    exx
    ld (iy+1+offset_increments),l
    ld (iy+2+offset_increments),h
    exx
    ret

; fetch DED'E'B floating point number from a 40-bit buffer
; inputs: iy = buffer address
; outputs: DED'E'B = floating point number
; destroys: DED'E'B
fetch_float_increments_alt:
    ld b,(iy+0+offset_increments)
    ld e,(iy+3+offset_increments)
    ld d,(iy+4+offset_increments)
    exx
    ld e,(iy+1+offset_increments)
    ld d,(iy+2+offset_increments)
    exx
    ret

; @command: asciz "flower 3.93 1.98 .6 66 .8 512 90"
command0: db "flower " 
command1: blkb 256-7,0 

    include "basic/ram.asm" ; must be last so that RAM has room for BASIC operations