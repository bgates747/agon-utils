    include "basic/ram.asm"
    include "basic/fpp.asm"

; --------------------------- from basic/eval.asm ---------------------------
;
; Title:	BBC Basic Interpreter - Z80 version
;		Expression Evaluation & Arithmetic Module - "EVAL"
; Author:	(C) Copyright  R.T.Russell  1984
; Modified By:	Dean Belfield
; Created:	12/05/2023
; Last Updated:	17/08/2023
;
; Modinfo:
; 07/06/2023:	Modified to run in ADL mode
; 26/06/2023:	Fixed HEX and HEXSTR
; 13/08/2023:	Added INKEY(-n) support (requires MOS 1.04)
; 17/08/2023:	Added binary constants
;
;Function STR - convert numeric value to ASCII string.
;   Inputs: HLH'L'C = integer or floating-point number.
;  Outputs: String in string accumulator.
;           E = length, D = ACCS/256
;           A = 80H (type=string)
;
;First normalise for decimal output:
;
STRS:			CALL    NXT
			CP      '~'
			JR      Z,HEXSTS
			CALL    ITEMN
			LD      IX,STAVAR
			LD      A,(IX+3)
			OR      A
			LD      IX,G9-1         ;G9 FORMAT
			JR      Z,STR0
STR:			LD      IX,STAVAR
STR0:			LD      DE,ACCS
			LD      A,37
			CALL    FPP
			JP      C,ERROR_
			BIT     0,(IX+2)
STR1:			LD      A,80H           ;STRING MARKER
			RET     Z
			LD      A,C
			ADD     A,4
STR2:			CP      E
			JR      Z,STR1
			EX      DE,HL	
			LD      (HL),' '        ;TRAILING SPACE
			INC     HL
			EX      DE,HL
			JR      STR2
;
G9:			DW    9


;HEXSTR - convert numeric value to HEX string.
;   Inputs: HLH'L'C = integer or floating-point number
;  Outputs: String in string accumulator.
;           E = string length.  D = ACCS/256
;
HEXSTS:			INC     IY              ;SKIP TILDE
			CALL    ITEMN
			CALL    HEXSTR
			LD      A,80H
			RET
;
HEXSTR:			CALL    SFIX
			LD      BC,8
			LD      DE,ACCS
HEXST1:			PUSH    BC
			LD      B,4
			XOR     A
HEXST2:			EXX
			ADD.S	HL,HL
			EXX
			ADC.S	HL,HL
			RLA
			DJNZ    HEXST2
			POP     BC
			DEC     C
			RET     M
			JR      Z,HEXST3
			OR      A
			JR      NZ,HEXST3
			CP      B
			JR      Z,HEXST1
HEXST3:			ADD     A,90H
			DAA
			ADC     A,40H
			DAA
			LD      (DE),A
			INC     DE
			LD      B,A
			JR      HEXST1

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
DISPT2:			PUSH    HL
			LD      HL,SOPTBL
			JR      DISPT0
;
DISPAT:			PUSH    HL
			SUB     FUNTOK
			LD      HL,FUNTBL
DISPT0:			PUSH    BC
			
			LD	BC, 3
			LD	B, A
			MLT	BC
			ADD	HL, BC
			LD	HL, (HL)

;			ADD     A,A
;			LD      C,A
;			LD      B,0
;			ADD     HL,BC
;			LD      A,(HL)
;			INC     HL
;			LD      H,(HL)
;			LD      L,A

			POP     BC
			EX      (SP),HL
			RET                     ;OFF TO ROUTINE




; Evaluate a numeric expression
;
EXPRN:			CALL    EXPR			; Evaluate expression
			EX      AF,AF'			; Get the type
			RET     P			; And return if it is a number
			JR      TYPE_			; Otherwise Error: "Type mismatch"
;
; Evaluate a fixed-point expression 
;
EXPRI:			CALL    EXPR			; Evaluate the expression
			EX      AF,AF'			; Get the type
			JP      P,SFIX			; If it is numeric, then convert to fixed-point notation
			JR      TYPE_			; Otherwise Error: "Type mismatch"
;	
; Evaluate a string expression
;	
EXPRS:			CALL    EXPR			; Evaluate the expression
			EX      AF,AF'			; Get the type
			RET     M			; And return if it is a string
			JR      TYPE_			; Otherwise Error: "Type mismatch"
;
; Get a numeric variable
;
ITEMN:			CALL    ITEM			; Get the variable
			OR      A			; Test the type
			RET     P			; And return if it is a number
			JR      TYPE_			; Otherwise Error: "Type mismatch"
;
; Get a fixed-point variable 
;
ITEMI:			CALL    ITEM			; Get the variable
			OR      A			; Test the type
			JP      P,SFIX			; If it is numeric, then convert to fixed-point notation
			JR      TYPE_			; Otherwise Error: "Type mismatch"
;
; Get a string variable 
;
ITEMS:			CALL    ITEM			; Get the variable
			OR      A			; Test the type
			RET     M			; If it is a string, then return
;							; Otherwise
TYPE_:			LD      A,6			; Error: "Type mismatch"
			JP      ERROR_      