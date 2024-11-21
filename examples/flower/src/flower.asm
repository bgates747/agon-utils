;
; Title:	flower
; Author:	Brandon R. Gates (BeeGee747)
; Created:	Nov. 2024
;
; This program draws 2D curves related to the epitrochoid family (i.e. Spirographs),
; more generally known as roulettes. However, instead of an outer wheel rolling
; around on an inner wheel, this algorithm can be thought of as a rotating arm whose
; radius oscillates a set number of times per rotation, which is set by the petals parameter.
; Unlike the Spirograph toy which plots a continuous curve, the vectors parameter determines
; the number of points plotted per oscillation. Specifying a small number of vectors leads 
; to more angular polygonal type curves remniscent of string art. Also unlike the toy, 
; a shrink factor can be specified resulting in graphs which are true spirals.
;
; More information about epitrochoid curves can be found here: 
; https://mathcurve.com/courbes2d.gb/epitrochoid/epitrochoid.shtml
; 
; Parameters with example values:
; petals       = 3.03  : Number radius oscillations per cycle.
; vectors      = 1.98  : Number of points plotted per oscillation.
; depth        = 0.6   : Multiplier determining the depth of the oscillation.
; periods      = 66    : Number of full rotations.
; shrink       = 0.8   : Multiplier determining the final radius relative to the start.
; theta_init   = 0.0   : Starting angle of the drawing cursor relative to the origin.
; radius_scale = 512   : Starting radius.
;
; ========================================
; MOSLET INITIALIZATION CODE
; ========================================
;
    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "flower"
    ENDMACRO
;
; Start in ADL mode
;
			JP	_start	
;
; The header stuff is from byte 64 onwards
;
_exec_name:
			PROGNAME			; The executable name, only used in argv

			ALIGN	64
			
			DB	"MOS"			; Flag for MOS - to confirm this is a valid MOS command
			DB	00h			; MOS header version 0
			DB	01h			; Flag for run mode (0: Z80, 1: ADL)
;
; And the code follows on immediately after the header
;
_start:			
            PUSH	AF			; Preserve the registers
			PUSH	BC
			PUSH	DE
			PUSH	IX
			PUSH	IY
			LD	A, MB			; Save MB
			PUSH 	AF
			XOR 	A
			LD 	MB, A                   ; Clear to zero so MOS API calls know how to use 24-bit addresses.

			CALL		_clear_ram ; Clear the BASIC memory allocation

			LD	IX, argv_ptrs		; The argv array pointer address
			PUSH	IX
			CALL	_parse_params		; Parse the parameters
			POP	IX			; IX: argv	
			LD	B, 0			;  C: argc
			CALL	_main_init			; Start user code
			
			POP 	AF
			LD	MB, A
			POP	IY			; Restore registers
			POP	IX
			POP	DE
			POP	BC
			POP	AF
			RET

; Parse the parameter string into a C array
; Parameters
; - HL: Address of parameter string
; - IX: Address for array pointer storage
; Returns:
; -  C: Number of parameters parsed
;
_parse_params:		LD	BC, _exec_name
			LD	(IX+0), BC		; ARGV[0] = the executable name
			LEA     IX, IX+3
			CALL	_skip_spaces		; Skip HL past any leading spaces
;
			LD	BC, 1			; C: ARGC = 1 - also clears out top 16 bits of BCU
			LD	B, argv_ptrs_max - 1	; B: Maximum number of argv_ptrs
;
_parse_params_1:	
			PUSH	BC			; Stack ARGC	
			PUSH	HL			; Stack start address of token
			CALL	_get_token		; Get the next token
			LD	A, C			; A: Length of the token in characters
			POP	DE			; Start address of token (was in HL)
			POP	BC			; ARGC
			OR	A			; Check for A=0 (no token found) OR at end of string
			RET	Z
;
			LD	(IX+0), DE		; Store the pointer to the token
			PUSH	HL			; DE=HL
			POP	DE
			CALL	_skip_spaces		; And skip HL past any spaces onto the next character
			XOR	A
			LD	(DE), A			; Zero-terminate the token
			LEA  	IX, IX+3			; Advance to next pointer position
			INC	C			; Increment ARGC
			LD	A, C			; Check for C >= A
			CP	B
			JR	C, _parse_params_1	; And loop
			RET

; Get the next token
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of first character after token
; -  C: Length of token (in characters)
;
_get_token:		LD	C, 0			; Initialise length
@@:			LD	A, (HL)			; Get the character from the parameter string
			OR	A			; Exit if 0 (end of parameter string in MOS)
			RET 	Z
			CP	13			; Exit if CR (end of parameter string in BBC BASIC)
			RET	Z
			CP	' '			; Exit if space (end of token)
			RET	Z
			INC	HL			; Advance to next character
			INC 	C			; Increment length
			JR	@B
	
; Skip spaces in the parameter string
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of next none-space character
;    F: Z if at end of string, otherwise NZ if there are more tokens to be parsed
;
_skip_spaces:		LD	A, (HL)			; Get the character from the parameter string	
			CP	' '			; Exit if not space
			RET	NZ
			INC	HL			; Advance to next character
			JR	_skip_spaces		; Increment length

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
			RET

; ========================================
; BEGIN APPLICATION CODE
; ========================================

; API INCLUDES
    include "basic/fpp.asm"
    include "functions.inc"
	include "maths.inc"
    include "mathfpp.inc"
    include "vdu.inc"
    include "vdu_plot.inc"
    include "files.inc"

; APPLICATION INCLUDES

; Storage for the argv array pointers
min_args: equ 1
argv_ptrs_max:		EQU	16			; Maximum number of arguments allowed in argv
argv_ptrs:		    BLKP	argv_ptrs_max, 0		
_sps:			DS	3			; Storage for the stack pointer (used by BASIC)

; Storage for the arguments, ORDER MATTERS
arg1: ds 5
arg2: ds 5

; GLOBAL MESSAGE STRINGS
str_usage: ASCIZ "Usage: scratch <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; GLOBAL VARIABLES / DEFAULTS
; ---- input arguments (float) ----
input_params_num: equ 7
input_params:
petals:             db   0x81, 0x1F, 0x85, 0xEB, 0x41 ; 3.03
vectors:            db   0x80, 0xD7, 0xA3, 0x70, 0x7D ; 1.98
depth:              db   0x7F, 0x9A, 0x99, 0x99, 0x19 ; 0.6
periods:            db   0x00, 0x42, 0x00, 0x00, 0x00 ; 66.0
shrink:             db   0x7F, 0xCC, 0xCC, 0xCC, 0x4C ; 0.8
radius_scale: 	    db   0x00, 0x00, 0x02, 0x00, 0x00 ; 512.0
theta_init: 	    db   0x00, 0x00, 0x00, 0x00, 0x00 ; 0

; ---- main loop constants (float unless noted otherwise) ----
step_theta_prime:   blkb 5,0    ; Step increment for theta_prime in each loop iteration
step_theta_petal:   blkb 5,0    ; Step increment for theta_petal in each loop iteration
total_steps:        blkb 5,0    ; Total number of iterations based on periods and step_theta_prime
step_shrink:        blkb 5,0    ; Step decrement applied to radius in each iteration

; ---- main loop state variables (float) ----
theta_prime: 	    blkb 5,0    ; Angle of the drawing cursor relative to the origin
theta_petal: 	    blkb 5,0    ; Angle used to compute radius offset of the petal circle
radius_prime:       blkb 5,0    ; Initial radius before shrink factor is applied
radius_petal:       blkb 5,0    ; Radius of the petal circle
radius:             blkb 5,0    ; Total radius of the curve
x_prev:             blkb 5,0    ; Previous x coordinate
y_prev:             blkb 5,0    ; Previous y coordinate

; ========= MAIN LOOP ========= 
; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK

_main_init:
    ld a,c              ; how many arguments?
    cp min_args         ; not enough?
    jr nc,main          ; if enough, go to main loop
    ld hl,str_usage     ; if not enough, print usage
    call printString
                        ; fall through to _main_end_error

_main_end_error:
    ld hl,str_error     ; print error message
    call printString
    ld hl,19            ; return error code 19
    ret

; begin BASIC-specific end code
; This bit of code is called from STAR_BYE and returns us safely to MOS
_end:			LD		SP, (_sps)		; Restore the stack pointer 
; fall through to _main_end_ok
; end BASIC-specific end code

_main_end_ok:
    ; call printNewLine
    ; ld hl,str_success   ; print success message
    ; call printString
    call printNewLine
    ld hl,0             ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:    
    dec c               ; decrement the argument count to skip the program name
    call load_input     ; load the input arguments
    call vdu_cls        ; clear the screen
    call print_input    ; print the input arguments

; Set screen origin to the center
    ld bc,1280/2 ; x
    ld de,1024/2 ; y
    call vdu_set_gfx_origin

; --- convert input thetas to radians
    ld iy,theta_prime
    call fetch_float_iy_nor
    ld a,rad
    call FPP
    call store_float_iy_nor

    ld iy,theta_petal
    call fetch_float_iy_nor
    ld a,rad
    call FPP
    call store_float_iy_nor

    ld iy,theta_init
    call fetch_float_iy_nor
    ld a,rad
    call FPP
    call store_float_iy_nor

    ld iy,theta_prime ; set theta_prime to theta_init
    call store_float_iy_nor

; --- compute the main loop parameters ---
; step_theta_prime = 2 * pi / (petals * vectors)
    ld iy,petals
    call fetch_float_iy_nor
    ld iy,vectors
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = petals * vectors

    call pi2_alt ; DED'E'B = 2 * pi
    call SWAP ; HLH'L'C <--> DED'E'B
    ld a,fdiv
    call FPP ; HLH'L'C = 2 * pi / (petals * vectors)
    ld iy,step_theta_prime
    call store_float_iy_nor

; step_theta_petal = 2 * pi / vectors
    ld iy,vectors
    call fetch_float_iy_nor
    call pi2_alt ; DED'E'B = 2 * pi
    call SWAP ; HLH'L'C <--> DED'E'B
    ld a,fdiv
    call FPP ; HLH'L'C = 2 * pi / vectors
; fmod rounds to the nearest integer, so we leave it out until we can find a better solution
    ; call pi2_alt ; DED'E'B = 2 * pi
    ; ld a,fmod
    ; call FPP ; HLH'L'C = 2 * pi % vectors
    ld iy,step_theta_petal
    call store_float_iy_nor

; total_steps = int(petals * vectors * periods)
    ld iy,petals
    call fetch_float_iy_nor
    ld iy,vectors
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = petals * vectors

    ld iy,periods
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = petals * vectors * periods
    ld iy,total_steps
    call store_float_iy_nor ; we'll make it an integer after computing step_shrink

; Initialize radius_prime accounting for depth
    LOAD_FLOAT "1"
    ld iy,depth
    call fetch_float_iy_alt
    ld a,fadd
    call FPP ; HLH'L'C = 1 + depth
    call SWAP ; DED'E'B = 1 + depth
    ld iy,radius_scale
    call fetch_float_iy_nor
    ld a,fdiv
    call FPP ; HLH'L'C = radius_scale / (1 + depth)
    ld iy,radius_prime
    call store_float_iy_nor

; Calculate shrink per step (linear)
    ; step_shrink = -shrink * radius_scale / total_steps 
    ld iy,shrink
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = shrink * radius_prime
    ld iy,total_steps
    call fetch_float_iy_alt
    ld a,fdiv
    call FPP ; HLH'L'C = shrink * radius_scale / total_steps

    ; call NEG_ ; HLH'L'C = -shrink * radius_scale / total_steps
; NEG_ is not working as expected, so we'll just subtract from zero
    call SWAP
    LOAD_FLOAT "0"
    ld a,fsub
    call FPP ; HLH'L'C = -shrink * radius_scale / total_steps
    ld iy,step_shrink
    call store_float_iy_nor

; Make total_steps an integer and store it in uhl
    ld iy,total_steps
    call fetch_float_iy_nor
    call int2hlu ; UHL = int(total_steps)
    ld (iy),hl

; set initial point and move graphics cursor to it
    call calc_point ; HLH'L'C = x DED'E'B = y

    ld a,plot_pt+mv_abs
    call vdu_plot_float

; fall through to main loop

@loop:
; Advance thetas
    ; theta_prime += step_theta_prime
    ld iy,step_theta_prime
    call fetch_float_iy_nor
    ld iy,theta_prime
    call fetch_float_iy_alt
    ld a,fadd
    call FPP ; HLH'L'C = theta_prime + step_theta_prime
    call store_float_iy_nor ; theta_prime

    ; theta_petal += step_theta_petal
    ld iy,step_theta_petal
    call fetch_float_iy_nor
    ld iy,theta_petal
    call fetch_float_iy_alt
    ld a,fadd
    call FPP ; HLH'L'C = theta_petal + step_theta_petal
    call store_float_iy_nor ; theta_petal

; Update radius_prime
    ; radius_prime += step_shrink
    ld iy,step_shrink
    call fetch_float_iy_nor
    ld iy,radius_prime
    call fetch_float_iy_alt
    ld a,fadd
    call FPP ; HLH'L'C = radius_prime + step_shrink
    call store_float_iy_nor ; radius_prime

; Calculate new coordinates and draw a line from the previous point
    call calc_point ; HLH'L'C = x DED'E'B = y
    ld a,plot_sl_both+dr_abs_fg ; plot mode
    call vdu_plot_float

; Decrement the loop counter
    ld hl,(total_steps)
    ld de,-1
    and a ; clear carry
    adc hl,de
    ld (total_steps),hl
    jp p,@loop

    jp _main_end_ok

; VDU 25, mode, x; y;: PLOT command
; inputs: a=mode, HL'H'L'C=x, DE'D'E'B=y
vdu_plot_float:
    ld (@mode),a

    call int2hlu
    ld (@x0),hl

    call SWAP
    call int2hlu
    ld (@y0),hl

	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:   db 25
@mode:  db 0
@x0: 	dw 0
@y0: 	dw 0
@end:   db 0 ; padding

; compute the Cartesian coordinates of the next point on the curve
; inputs: theta_prime, theta_petal, radius_prime, depth
; outputs: HLH'L'C = x, DED'E'B = y
calc_point:
; Calculate the petal radius and total radius 
    ; radius_petal = math.cos(theta_petal) * depth
    ld iy,theta_petal
    call fetch_float_iy_nor
    ld a,cos
    call FPP ; HLH'L'C = cos(theta_petal)
    ld iy,depth
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = radius_petal

    ; radius = radius_prime + radius_petal * radius_prime
    ld iy,radius_prime
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = radius_petal * radius_prime
    ld iy,radius_prime
    call fetch_float_iy_alt
    ld a,fadd
    call FPP ; HLH'L'C = radius
    call SWAP ; DED'E'B = radius

; Convert polar to Cartesian coordinates
    ld iy,theta_prime
    call fetch_float_iy_nor ; HLH'L'C = theta_prime
    call polar_to_cartesian_fpp ; HLH'L'C = x, DED'E'B = y

    ret

; --- Load arguments ---
; --------------------------------
load_input:
    ld b,input_params_num ; loop counter assuming correct number of arguments were entered
    ld a,c ; number of arguments entered
    sub b ; compare expected with entered
    jp p,@F ; entered arguments >= expected, so proceed ignoring any excess arguments
    add a,b ; set loop counter to entered arguments
    ret z ; no arguments entered so return, leaving all to defaults
    ld b,a
@@:
    ld iy,input_params  ; point to the arguments table
@loop:
    push bc ; save the loop counter
    call store_arg_iy_float ; get the next argument and store it
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

print_input:
    ld b,input_params_num ; loop counter = number of arguments
    ld iy,input_params  ; point to the arguments table
@loop:
    push bc ; save the loop counter
    call fetch_float_iy_nor ; fetch the next parameter into HLH'L'C
    call print_float_dec_nor ; print the parameter
    ld a,' ' ; print a space separator
    rst.lil $10
    lea iy,iy+5  ; point to the next parameter
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    ret

; --- Specific parameter processing functions ---
args_count_off:
    ld hl,@str_args_count_off
    call printString
    jp _main_end_error
@str_args_count_off: db "Argument counts mismatch!\r\n",0

; ---- text strings ----
str_step_theta_prime: ASCIZ "step_theta_prime: "
str_step_theta_petal: ASCIZ "step_theta_petal: "
str_total_steps: ASCIZ "total_steps: "
str_step_shrink: ASCIZ "step_shrink: "

str_theta_prime: ASCIZ "theta_prime: "
str_radius_prime: ASCIZ "radius_prime: "
str_radius_petal: ASCIZ "radius_petal: "
str_theta_petal: ASCIZ "theta_petal: "

str_radius: ASCIZ "radius: "
str_xy: ASCIZ "x,y: "

; ========== HELPER FUNCTIONS ==========
;
; get the next argument after ix as a floating point number
; inputs: ix = pointer to the argument string
; outputs: HLH'L'C = floating point number, ix points to the next argument
; destroys: everything except iy, including prime registers
get_arg_float:
    lea ix,ix+3 ; point to the next argument
    push ix ; preserve
    ld ix,(ix)  ; point to argument string
    call val_fp ; convert the string to a float
    pop ix ; restore
    ret ; return with the value in HLH'L'C

; get the next argument after ix as a floating point number and store it in buffer pointed to by iy
; inputs: ix = pointer to the argument string
; outputs: HLH'L'C = floating point number, ix points to the next argument
; destroys: everything except iy, including prime registers
store_arg_iy_float:
    lea ix,ix+3 ; point to the next argument
    push ix ; preserve
    ld ix,(ix)  ; point to argument string
    call val_fp ; convert the string to a float
    call store_float_iy_nor ; save the float in buffer
    pop ix ; restore
    ret ; return with the value in HLH'L'C
;
; get the next argument after ix as a string
; inputs: ix = pointer to the argument string
; outputs: HL = pointer to the argument string, ix points to the next argument
; destroys: a, h, l, f
get_arg_text:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    ret
;
; match the next argument after ix to the dispatch table at iy
;   - arguments and dispatch entries are zero-terminated, case-sensitive strings
;   - final entry of dispatch table must be a 3-byte zero or bad things will happen
; returns: NO MATCH: iy=dispatch list terminator a=1 and zero flag reset
;          ON MATCH: iy=dispatch address, a=0 and zero flag set
; destroys: a, hl, de, ix, iy, flags
match_next:
    lea ix,ix+3         ; point to the next argument
@loop:
    ld hl,(iy)          ; pointer argument dispatch record
    sign_hlu            ; check for list terminator
    jp z,@no_match      ; if a=0, return error
    inc hl              ; skip over jp instruction
    inc hl
    ld de,(ix)          ; pointer to the argument string
    call str_equal      ; compare the argument to the dispatch table entry
    jp z,@match         ; if equal, return success
    lea iy,iy+3         ; if not equal, bump iy to next dispatch table entry
    jp @loop            ; and loop 
@no_match:
    inc a               ; no match so return a=1 and zero flag reset
    ret
@match:
    ld iy,(iy)          ; get the function pointer
    ret                 ; return a=0 and zero flag set

; same as match_next, but prints the parameter if a match is found
match_next_and_print:
    call match_next
    ret nz ; no match found
    lea ix,ix-3 
    call get_arg_text ; hl points to the operator string
    call print_param
    ret

; compare two zero-terminated strings for equality, case-sensitive
; hl: pointer to first string, de: pointer to second string
; returns: z if equal, nz if not equal
; destroys: a, hl, de
str_equal:
    ld a,(de)           ; get the first character
    cp (hl)             ; compare to the second character
    ret nz              ; if not equal, return
    or a
    ret z               ; if equal and zero, return
    inc hl              ; next character
    inc de
    jp str_equal        ; loop until end of string

; print the parameter string pointed to by ix
; destroys: a, hl
print_param:
    ld hl,(ix)          ; get the parameter pointer
    call printString    ; print the parameter string
    ld a,' '            ; print a space separator
    rst.lil $10         
    ret

; print the parameters
; inputs: b = number of parameters, ix = pointer to the parameters
; destroys: a, hl, bc
print_params:
    ld b,c              ; loop counter = number of parameters
    push ix             ; save the pointer to the parameters
@loop:
    push bc             ; save the loop counter
    call print_param    ; print the parameter
    lea ix,ix+3         ; next parameter pointer
    pop bc              ; get back the loop counter
    djnz @loop          ; loop until done
    pop ix              ; restore the pointer to the parameters
    ret

    include "basic/ram.asm" ; must be last so that RAM has room for BASIC operations