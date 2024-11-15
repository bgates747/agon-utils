	include "basic/fpp.asm"

; =================================================================================================
; FROM eval.asm
; -------------------------------------------------------------------------------------------------
;
;VAL - Return numeric value of string.
;Result is variable type numeric.
;
VAL:			CALL    ITEMS
VAL0:			XOR     A
			LD      (DE),A
			LD      IX,ACCS
			LD      A,36
			JR      FPP1

; Get a string variable 
;
ITEMS:			CALL    ITEM			; Get the variable
			OR      A			; Test the type
			RET     M			; If it is a string, then return
;							; Otherwise
TYPE_EV_:			LD      A,6			; Error: "Type mismatch"
			JP      ERROR_     

FPP1:			CALL    FPP
			JP      C,ERROR_
			XOR     A
			RET

;
; ITEM - VARIABLE TYPE NUMERIC OR STRING ITEM.
; Item type is returned in A:  Bit 7=0 numeric.
;                              Bit 7=1 string.
; Numeric item returned in HLH'L'C.
; String item returned in string accumulator,
;   DE addresses byte after last (E=length).
;
ITEM:			CALL    CHECK			; Check there's at least a page of free memory left and Error: "No room" if not
			CALL    NXT			; Skip spaces
			INC     IY			; Move to the prefix character
			CP      '&'			; If `&`
			JP      Z,HEX           	; Then get a HEX constant
			CP	'%'			; If '%'
			JR	Z,BIN			; Then get a BINARY constant
			CP      '-'			; If `-`
			JR      Z,MINUS         	; Then get a negative number
			CP      '+'			; If `+`
			JP      Z,ITEMN         	; Then just fetch the number (unary plus)
			CP      '('			; If `(`
			JP      Z,ITEM1         	; Start of a bracketed expression
			CP      34			; If `"`
			JR      Z,CONS          	; Start of a string constant
			CP      TCMD_EV			; Is it out of range of the function table?
			JP      NC,SYNTAX       	; Error: "Syntax Error"
			CP      FUNTOK			; If it is in range, then 
			JP      NC,DISPAT       	; It's a function
			DEC     IY			
			CP      ':'
			JR      NC,ITEM2		; VARIABLE?
			CP      '0'
			JP      NC,CON			; NUMERIC CONSTANT
			CP      '.'
			JP      Z,CON			; NUMERIC CONSTANT
ITEM2:			CALL    GETVAR			; VARIABLE
			JR      NZ,NOSUCH
			OR      A
			JP      M,LOADS			; STRING VARIABLE
LOADN:			OR      A
			JR      Z,LOAD1			; BYTE VARIABLE
			LD      C,0
			BIT     0,A
			JR      Z,LOAD4			; INTEGER VARIABLE
LOAD5:			LD      C,(IX+4)
LOAD4:			EXX
			LD	HL, 0			; TODO: Optimise
			LD      L,(IX+0)
			LD      H,(IX+1)
			EXX
			LD	HL, 0			; TODO: Optimise
			LD      L,(IX+2)
			LD      H,(IX+3)
			RET
;
LOAD1:			LD      HL,0
			EXX
			LD      HL,0			; TODO: Optimise
			LD      L,(IX+0)
			EXX
			LD      C,H
			RET
;
NOSUCH:			JP      C,SYNTAX
			LD      A,(LISTON)
			BIT     5,A
			LD      A,26
			JR      NZ,ERROR0_EV		; Throw "No such variable"
NOS1:			INC     IY
			CALL    RANGE
			JR      NC,NOS1
			LD      IX,PC
			XOR     A
			LD      C,A
			JR      LOAD4

; Skip spaces
; - IY: String pointer
; Returns:
;  - A: The non-space character found
; - IY: Points to the character before that
; 
NXT:			LD      A,(IY)			; Fetch the character	
			CP      ' '			; If it is space, then return
			RET     NZ
			INC     IY			; Increment the pointer and
			JP      NXT			; Loop

;
; HEX - Get hexadecimal constant.
;   Inputs: ASCII string at (IY)
;  Outputs: Integer result in H'L'HL, C=0, A7=0.
;           IY updated (points to delimiter)
;
HEX:			CALL    ZERO			; Set result to 0
			CALL    HEXDIG			; Fetch the character from IY
			JR      C,BADHEX		; If invalid HEX character, then Error: "Bad HEX"
HEX1:			INC     IY			; Move pointer to next character
			AND     0FH			; Clear the top nibble
			LD      B,4			; Loop counter
;
HEX2:			EXX				; Shift the result left B (4) times. This makes
			ADD.S   HL,HL			; space for the incoming nibble in the least significant 4 bits
			EXX				; .
			ADC.S   HL,HL			; .
			DJNZ    HEX2			; And loop
			EXX
			OR      L			; OR in the digit
			LD      L,A
			EXX
;
			CALL    HEXDIG			; Fetch the next character
			JR      NC,HEX1			; If it is a HEX digit then loop
			XOR     A			; Clear A
			RET
;
BADHEX:			LD      A,28
			JP      ERROR_          	; Error: "Bad HEX"

;
; BIN - Get binary constant.
;   Inputs: ASCII string at (IY)
;  Outputs: Integer result in H'L'HL, C=0, A7=0.
;           IY updated (points to delimiter)
;
BIN:			CALL    ZERO			; Set result to 0
			CALL	BINDIG			; Fetch the character from IY
			JR	C,BADBIN		; If invalid BIN character then Error: "Bad Binary"
BIN1:			INC	IY			; Move pointer to next character
			RRCA				; Bit 0 of ASCII '0' is 0, and ASCII '1' is 1, so shift that bit into carry
			EXX				; 
			ADC.S	HL,HL			; And shift back into into H'L'HL (note the ADC)
			EXX
			ADC.S	HL,HL
			CALL	BINDIG			; Fetch the next character
			JR	NC,BIN1
			XOR	A			; Clear A
			RET
;
BADBIN:			LD	A, 28			; Error: "Bad Binary" - reuses same error code as Bad HEX
			JP      ERROR_          


; =================================================================================================
; from exec.asm
; -------------------------------------------------------------------------------------------------
;
; Check whether the stack is full
;
CHECK:			PUSH    HL
			PUSH	BC
			LD      HL,(FREE)		; HL: Address of first free space byte
			LD	BC,100h			; BC: One page of memory
			ADD	HL,BC			; Add a page to FREE
			SBC     HL,SP			; And subtract the current SP
			POP	BC
			POP     HL
			RET     C			; The SP is not in the same page, so just return
			XOR     A			; Otherwise
			JP      ERROR_			; Throw error "No room"
;
STORS3:			LD	BC,0
			LD      C,E			; BC: String length
			PUSH    IX
			POP     DE			; DE: Destination
			XOR     A			; Check if string length is 0
			CP      C
			JR      Z,STORS5		; Yes, so don't copy
			LDIR
STORS5:			LD      A,CR			; Finally add the terminator
			LD      (DE),A
			RET


; =================================================================================================
; from ram.asm
; -------------------------------------------------------------------------------------------------

			ALIGN 		256		; ACCS, BUFFER & STAVAR must be on page boundaries			
RAM_START:		
;
ACCS:           BLKB    256,0             ; String Accumulator
BUFFER:         BLKB    256,0             ; String Input Buffer
STAVAR:         BLKB    27*4,0            ; Static Variables
DYNVAR:         BLKB    54*3,0            ; Dynamic Variable Pointers
FNPTR:          BLKB    3,0               ; Dynamic Function Pointers
PROPTR:         BLKB    3,0               ; Dynamic Procedure Pointers
;
PAGE_:          BLKB    3,0               ; Start of User Program
TOP:            BLKB    3,0               ; First Location after User Program
LOMEM:          BLKB    3,0               ; Start of Dynamic Storage
FREE:           BLKB    3,0               ; First Free Space Byte
HIMEM:          BLKB    3,0               ; First Protected Byte
;
LINENO:         BLKB    3,0               ; Line Number
TRACEN:         BLKB    3,0               ; Trace Flag
AUTONO:         BLKB    3,0               ; Auto Flag
ERRTRP:         BLKB    3,0               ; Error Trap
ERRTXT:         BLKB    2,0               ; Error Message Pointer
DATPTR:         BLKB    2,0               ; Data Pointer
ERL:            BLKB    2,0               ; Error Line
ERRLIN:         BLKB    3,0               ; The "ON ERROR" Line
RANDOM:         BLKB    5,0               ; Random Number
COUNT:          BLKB    1,0               ; Print Position
WIDTH:          BLKB    1,0               ; Print Width
ERR:            BLKB    1,0               ; Error Number
LISTON:         BLKB    1,0               ; LISTO (bottom nibble)
                                ; - BIT 0: If set, output a space after the line number
                                ; - BIT 1: If set, then indent FOR/NEXT loops
                                ; - BIT 2: If set, then indent REPEAT/UNTIL loops
                                ; - BIT 3: If set, then output to buffer for *EDIT
                                ; OPT FLAG (top nibble)
                                ; - BIT 4: If set, then list whilst assembling
                                ; - BIT 5: If set, then assembler errors are reported
                                ; - BIT 6: If set, then place the code starting at address pointed to by O%
                                ; - BIT 7: If set, then assemble in ADL mode, otherwise assemble in Z80 mode
INCREM:         BLKB    1,0               ; Auto-Increment Value
;
; --------------------------------------------------------------------------------------------
; BEGIN MODIFIED CODE
; --------------------------------------------------------------------------------------------
; Originally in equs.inc
;
OC:			EQU     15*4+STAVAR     ; CODE ORIGIN (O%)
PC:			EQU     16*4+STAVAR     ; PROGRAM COUNTER (P%)
VDU_BUFFER:		EQU	ACCS		; Storage for VDU commands
; --------------------------------------------------------------------------------------------
; END MODIFIED CODE
; --------------------------------------------------------------------------------------------

; Extra Agon-implementation specific system variables
;
FLAGS:          BLKB    1,0       ; Miscellaneous flags
                                ; - BIT 7: Set if ESC pressed
                                ; - BIT 6: Set to disable ESC
OSWRCHPT:       BLKB    2,0       ; Pointer for *EDIT
OSWRCHCH:       BLKB    1,0       ; Channel of OSWRCH
                                ; - 0: Console
                                ; - 1: File
OSWRCHFH:       BLKB    1,0       ; File handle for OSWRCHCHN
KEYDOWN:        BLKB    1,0       ; Keydown flag
KEYASCII:       BLKB    1,0       ; ASCII code of pressed key
KEYCOUNT:       BLKB    1,0       ; Counts every time a key is pressed
R0:             BLKB    3,0       ; General purpose storage for 8/16 to 24 bit operations
R1:             BLKB    3,0

;
; This must be at the end
;
RAM_END:
			ALIGN	256			
USER:							; Must be aligned on a page boundary
	