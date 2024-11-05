;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "flower.bin"
    ENDMACRO

; STANDARD MOSLET INCLUDES
    include "init.inc"
    include "parse.inc"

; API INCLUDES
    include "functions.inc"
    include "maths.inc"
	INCLUDE	"arith24.inc"
    include "trig24.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"

; APPLICATION INCLUDES
str_usage: ASCIZ "Usage: flower <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; This program draws 2D curves related to the hypotrochoid / epitrochoid family (i.e. Spirographs),
; more generally known as roulettes. While it is possible to construct curves fitting the precise
; definitions of such curves, the program is not limited to them as slipping of the outer circle
; is allowable. In addition, continually plotting the curve insribed by the outer circle is not required.
; This allows rotating polygonal shapes remniscent of string art, as well as daisy-like curves.
; Hence the name "flower" even though the program is not limited to such shapes.
; Another key difference is that cumulative shrinking can be applied to the radii of the rotating circles,
; thus allowing curves which form true spirals in contrast to the Spirograph toy, which does not.
; 
; Parameters with example values:
; petals      = 3.03  : 
; vectors     = 1.98  : 
; depth       = 0.6   : 
; periods     = 66    : 
; shrink      = 0.8   : 
; theta_prime = 0.0   : 
; radius_scale= 480   : 

; ========= BOILERPLATE MAIN LOOP ========= 
; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK

min_args: equ 2

_main:
    ld a,c              ; how many arguments?
    cp min_args         ; not enough?
    jp nc,main          ; if enough, go to main loop
    ld hl,str_usage     ; if not enough, print usage
    call printString
                        ; fall through to _main_end_error

_main_end_error:
    ld hl,str_error     ; print error message
    call printString
    ld hl,19            ; return error code 19
    ret

_main_end_ok:
    ; ld hl,str_success   ; print success message
    ; call printString
    call printNewLine
    ld hl,0             ; return 0 for success
    ret

; GLOBAL VARIABLES / DEFAULTS
; ---- input arguments (16.8 fixed) ----
input_params_num: equ 5
input_params:               ; label so we can traverse the table in loops
petals: 	    dl 0x000307	; 3.03
vectors: 	    dl 0x0001FA	; 1.98
depth: 	        dl 0x000099	; 0.6
periods: 	    dl 0x004200	; 66
shrink: 	    dl 0x0000CC	; 0.8
clock_prime: 	dl 0x000100	; 1
clock_petal: 	dl 0x000100	; 1
theta_prime: 	dl 0x000000	; 0
theta_petal: 	dl 0x000000	; 0
; radius_scale: 	dl 0x01E000	; 480
radius_scale: 	dl 0x010000 ; 256

; ---- main loop parameters (16.8 fixed) ----
step_theta_prime:   dl 0x000000  ; Step increment for theta_prime in each loop iteration
step_theta_petal:   dl 0x000000  ; Step increment for theta_petal in each loop iteration
total_steps:        dl 0x000000  ; Total number of iterations based on periods and step_theta_prime
shrink_step:        dl 0x000000  ; Step decrement applied to radius in each iteration

; ---- main loop state variables (16.8 fixed) ----
radius_prime:       dl 0x000000  ; Initial radius before shrink factor is applied
x_prev:             dl 0x000000  ; Previous x coordinate
y_prev:             dl 0x000000  ; Previous y coordinate

main_loop:
; --- clear the screen ---
    call vdu_cls

; --- convert input thetas to 16.8 fixed point degrees255
    ld hl,(theta_prime) ; get the theta_prime value
    call deg_360_to_256 ; convert to 16.8 fixed point
    ld (theta_prime),hl ; store the result

    ld hl,(theta_petal) ; get the theta_petal value
    call deg_360_to_256 ; convert to 16.8 fixed point
    ld (theta_petal),hl ; store the result

; --- compute the main loop parameters ---
; step_theta_prime = 256 degrees / (petals * vectors)
    ld hl,(petals) 
    ld de,(vectors)
    call umul168 ; uh.l = petals * vectors
    ex de,hl ; de = petals * vectors
    ld hl,256*256 ; 360 degrees in 16.8 fixed point
    call udiv168 ; ud.e = 256 / (petals * vectors)
    ld (step_theta_prime),de ; store the result
;    call print_hex_de
;    call print_s168_de
;    call printNewLine

; step_theta_petal = 256 degrees / vectors
    ld hl,256*256 ; 360 degrees in 16.8 fixed point
    ld de,(vectors)
    call udiv168 ; ud.e = 256 / vectors
    ld (step_theta_petal),de ; store the result
;    call print_hex_de
;    call print_s168_de
;    call printNewLine

; total_steps = int(256 degrees / step_theta_prime * periods)
    ld hl,256*256 ; 360 degrees in 16.8 fixed point
    ld de,(step_theta_prime)
    call udiv168 ; ud.e = 256 / step_theta_prime
    ld hl,(periods)
    call umul168 ; uh.l = periods * 256 / step_theta_prime
    call hlu_udiv256 ; we only want the integer part
    ld (total_steps),hl ; store the result
    ; call print_hex_hl
    ; call printDec
    ; call printNewLine

; Calculate shrink per step (linear)
    ; shrink_step = -shrink / total_steps
    ex de,hl ; de = total_steps
    ld hl,(shrink)
    call neg_hlu
    call sdiv168 ; ud.e = -shrink / total_steps
    ld (shrink_step),de ; store the result
;    call print_hex_de
;    call print_s168_de
;    call printNewLine

; ; Initialize radius_prime
;     ; radius_prime = (1 - (depth / 2)) * radius_scale
;     ld hl,(depth)
;     ld de,1
;     call shr_hlu ; uh.l = depth / 2
;     ex de,hl ; de = depth / 2
;     ld hl,1*256 ; 1 in 16.8 fixed point
;     or a ; clear carry
;     sbc hl,de ; uh.l = 1 - depth / 2
;     ld de,(radius_scale)
;     call smul168 ; uh.l = (1 - depth / 2) * radius_scale
;     ld (radius_prime),hl ; store the result
;     ; call print_hex_hl
;     ; call print_s168_hl
;     ; call printNewLine
    ld hl,(radius_scale)
    ld (radius_prime),hl

; Set screen origin to the center
    ld bc,1280/2 ; x
    ld de,1024/2 ; y
    call vdu_set_gfx_origin

; set initial point and move graphics cursor to it
    call calc_point ; ub.c = x, ud.e = y
    ld a,plot_pt+mv_abs ; plot mode
    call vdu_plot_168
    ; fall through to main loop

@loop:
    ; Advance theta values
        ; theta_prime += step_theta_prime
        ld hl,(theta_prime)
        ld de,(step_theta_prime)
        add hl,de
        ld (theta_prime),hl
        ; theta_petal += step_theta_petal
        ld hl,(theta_petal)
        ld de,(step_theta_petal)
        add hl,de
        ld (theta_petal),hl

    ; Update radius_prime
        ; radius_prime += shrink_step
        ld hl,(radius_prime)
        ld de,(shrink_step)
        add hl,de
        ld (radius_prime),hl

    ; Calculate new coordinates and draw a line from the previous point
        call calc_point ; ub.c = x, ud.e = y
        ld a,plot_sl_both+dr_abs_fg ; plot mode
        call vdu_plot_168

    ; Decrement the loop counter
        ld hl,total_steps
        dec (hl)
        jp nz,@loop
    ret

; compute the Cartesian coordinates of the next point on the curve
; inputs: theta_prime, theta_petal, radius_prime, depth
; outputs: ub.c = x, ud.e = y
calc_point:
; Calculate the petal radius and total radius 
    ; radius_petal = math.cos(theta_petal) * depth
    ld hl,(theta_petal)
    call cos168 ; uh.l = cos(theta_petal)
    ld de,(depth)
    call smul168 ; uh.l = radius_petal

    ; radius = radius_prime + radius_petal * radius_prime
    ld de,(radius_prime)
    call smul168 ; uh.l = radius_petal * radius_prime
    add hl,de ; uh.l = radius_prime + radius_petal * radius_prime
    ex de,hl ; de = radius

; Convert polar to Cartesian coordinates
    ; x, y = polar_to_cartesian(radius, theta_prime)
    ld hl,(theta_prime)
    call polar_to_cartesian ; ub.c = x, ud.e = y

; ; Debug print
;     call print_hex_bc
;     call print_s168_bc
;     call print_hex_de
;     call print_s168_de
;     ; call printNewLine

; all done
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c               ; decrement the argument count to skip the program name
    call load_input     ; load the input arguments
    call main_loop      ; run the main loop
    jp _main_end_ok     ; exit with success

; --- Load arguments ---
; --------------------------------
load_input:
    ld a,c ; put the number of entered arguments in a
    ld b,input_params_num ; loop counter = number of arguments
    cp b ; compare the number of arguments to the number of arguments
    call nz,args_count_off ; handle discrepancies
    ; TODO: we may want to branch here according to the result
    ld iy,input_params  ; point to the arguments table
@loop:
        call get_arg_s168 ; get the next argument
        ld (iy),de ; store the argument in the table
        lea iy,iy+3  ; point to the next parameter
        djnz @loop ; loop until done
        ret

; --- Specific parameter processing functions ---
args_count_off:
    ld hl,@str_args_count_off
    call printString
    ret ; TODO: implement this
@str_args_count_off: db "Argument counts mismatch!\r\n",0


; ========== HELPER FUNCTIONS ==========
; get the next argument after ix as a signed 16.8 fixed point number
; inputs: ix = pointer to the argument string
; outputs: ude = signed 16.8 fixed point number
; destroys: a, d, e, h, l, f
get_arg_s168:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    call asc_to_s168 ; convert the string to a number
    ret ; return with the value in DE

; Inputs: ix = pointer to the argument string
; Outputs: ude = signed 24-bit integer
; Destroys: a, d, e, h, l, f
get_arg_s24:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    call asc_to_s24 ; convert the string to a number
    ret ; return with the value in DE

get_plot_coords:
; get the move coordinates
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the x coordinate string
    call asc_to_s168 ; de = x coordinate
    push de
    pop bc ; bc = x coordinate
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the y coordinate string
    call asc_to_s168 ; de = y coordinate
    ret

get_arg_text:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    ret

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

debug_print:
    call printNewLine   ; DEBUG
    call dumpFlags      ; DEBUG
    call print_param    ; DEBUG
    call printNewLine   ; DEBUG
    call printNewLine   ; DEBUG
    ret