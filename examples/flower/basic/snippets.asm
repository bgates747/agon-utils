
; from exec.asm
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
			; XOR     A			; Otherwise
			; JP      ERROR_			; Throw error "No room"
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


; from main.asm

; PUTVAR - CREATE VARIABLE AND INITIALISE TO ZERO.
;   Inputs: HL, IY as returned from GETVAR (NZ).
;  Outputs: As GETVAR.
; Destroys: everything
;
PUTVAR:			CALL    CREATE			; Create the variable
			LD      A,(IY)			; Fetch the next character
			CP      '('			; Check for bad use of array
			JR      NZ,GETVZ        	; It's fine, so set the exit conditions
ARRAY:			LD      A,14            	; Otherwise Error: 'Array'
ERROR3:			
            ; JP      ERROR_
;
;GETVAR - GET LOCATION OF VARIABLE, RETURN IN HL & IX
;   Inputs: IY addresses first character.
;  Outputs: Carry set and NZ if illegal character.
;           Z-flag set if variable found, then:
;            A = variable type (0,4,5,128 or 129)
;            HL = IX = variable pointer.
;            IY updated
;           If Z-flag & carry reset, then:
;            HL, IY set for subsequent PUTVAR call.
; Destroys: everything
;
GETVAR:			LD      A,(IY)			; Get the first character
			CP      '$'			; Is it a string?
			JR      Z,GETV4			; Yes, so branch here
			CP      '!'			; Is it indirection (32-bit)?
			JR      Z,GETV5			; Yes, so branch here
			CP      '?'			; Is it indirection (8-bit)?
			JR      Z,GETV6			; Yes, so branch here
;
			CALL    LOCATE			; Locate the variable
			RET     NZ			; And exit here if not found
;
; At this point:
;  HL: Address of variable in memory
;   D: Variable type (4 = Integer, 5 = Floating point, 129 = String)
;
			LD      A,(IY)			; Further checks
			CP      '('             	; Is it an array?
			JR      NZ,GETVX        	; No, so exit
;
; We are processing an array at this point
;
			PUSH    DE              	; Save the variable type (in D)
			LD      A,(HL)          	; Fetch the number of dimensions
			OR      A
			JR      Z,ARRAY			; If there are none, then Error: 'Array'
			INC     HL			; 
			LD      DE,0            	; Accumulator
			PUSH    AF
			INC     IY              	; Skip "("
			JR      GETV3
;
GETV2:			PUSH    AF
			CALL    COMMA
GETV3:			PUSH    HL
			PUSH    DE
			CALL    EXPRI			; Get the subscript
			EXX
			POP     DE			
			EX      (SP),HL
			LD      C,(HL)
			INC     HL
			LD      B,(HL)
			INC     HL
			EX      (SP),HL
			EX      DE,HL
			PUSH    DE			
			CALL    MUL16			; HL=HL*BC
			POP     DE			
			ADD     HL,DE			
			EX      DE,HL
			OR      A
			SBC     HL,BC
			LD      A,15
			JR      NC,ERROR3		; Throw a "Subscript" error
			POP     HL
			POP     AF
			DEC     A               	; Dimension counter
			JR      NZ,GETV2
			CALL    BRAKET          	; Check for closing bracket
			POP     AF              	; Restore the type
			PUSH    HL
			CALL    X4OR5           	; DE=DE*n
			POP     HL
			ADD     HL,DE
			LD      D,A             	; The type
			LD      A,(IY)
GETVX:			CP      '?'
			JR      Z,GETV9
			CP      '!'
			JR      Z,GETV8
GETVZ:			PUSH    HL              	; Set exit conditions
			POP     IX
			LD      A,D
			CP      A
			RET			
;
; Process strings, unary & binary indirection:
;
GETV4:			LD      A,128           	; Static strings
			JR      GETV7
;
GETV5:			LD      A,4             	; Unary 32-bit indirection
			JR      GETV7
;
GETV6:			XOR     A               	; Unary 8-bit indirection
;
GETV7:			LD      HL,0
			PUSH    AF
			JR      GETV0
;
GETV8:			LD      B,4             	; Binary 32-bt indirection
			JR      GETVA
;
GETV9:			LD      B,0             	; Binary 8-bit indirection
;
GETVA:			PUSH    HL
			POP     IX
			LD      A,D            		; Fetch the variable type
			CP      129			; Is it a string?
			RET     Z               	; Yes, so exit here
			PUSH    BC			
			CALL    LOADN           	; Left operand of the binary indirection (var?index or var!index)
			CALL    SFIX
			LD	A,L
			EXX
			LD	(R0+0),HL
			LD	(R0+2),A
			LD	HL,(R0)			; HL: 24-bit address of the variable in memory
;
GETV0:			PUSH    HL			; HL will be 0 for a unary indirection, or the address of the variable for a binary indirection
			INC     IY
			CALL    ITEMI
			LD	A,L			;  A: The MSB of the address
			EXX
			LD	(R0+0),HL		; HL: The LSW of the address
			LD	(R0+2),A		; R0: L'HL or the 24-bit address
			POP     DE
			POP     AF
			LD	HL,(R0)			; HL: L'HL
			ADD     HL,DE
			PUSH    HL
			POP     IX
			CP      A
			RET


; CREATE - CREATE NEW ENTRY, INITIALISE TO ZERO.
;   Inputs: HL, IY as returned from LOCATE (NZ).
;  Outputs: As LOCATE, GETDEF.
; Destroys: As LOCATE, GETDEF.
;
CREATE:			XOR     A				
			LD      DE,(FREE)		; Get the last byte of available RAM
			LD	(HL), DE		; Store 
			EX      DE,HL
			LD      (HL),A			; Clear the link of the new entity
			INC     HL
			LD      (HL),A
			INC     HL
			LD      (HL),A
			INC     HL
LOC7:			INC     IY
			CALL    RANGE           	; END OF VARIABLE?
			JR      C,LOC8
			LD      (HL),A
			INC     HL
			CALL    RANGE1
			JR      NC,LOC7
			CP      '('
			JR      Z,LOC8
			LD      A,(IY+1)
			CP      '('
			JR      Z,LOC7
			INC     IY
LOC8:			LD      (HL),0          	; TERMINATOR
			INC     HL
			PUSH    HL
			CALL    TYPE_			; Get the variable type in D
			LD      A,4			; If it is an integer then it takes up 4 bytes
			CP      D
			JR      Z,LOC9			; So skip the next bit
			INC     A			; Strings and floats take up 5 bytes (NB: Strings take up 4 in BBC BASIC for Z80)
LOC9:			LD      (HL),0          	; Initialise the memory to zero
			INC     HL
			DEC     A
			JR      NZ,LOC9
			LD      (FREE),HL		; Adjust the stack
			CALL    CHECK			; Check whether we are out of space
			POP     HL
			XOR     A
			RET


; LOCATE - Try to locate variable name in static or dynamic variables.
; If illegal first character return carry, non-zero.
; If found, return no-carry, zero.
; If not found, return no-carry, non-zero.
;   Inputs: IY=Addresses first character of name.
;            A=(IY)
;  Outputs:  F=Z set if found, then:
;           IY=addresses terminator
;           HL=addresses location of variable
;            D=type of variable: 4 = integer
;                                5 = floating point
;                              129 = string
; Destroys: A,D,E,H,L,IY,F
;
; Variable names can start with any letter of the alphabet (upper or lower case), underscore (_), or the grave accent (`)
; They can contain any alphanumeric character and underscore (_)
; String variables are postfixed with the dollar ($) character
; Integer variables are postfixed with the percent (%) character
; Static integer variables are named @%, A% to Z%
; All other variables are dynamic
;
LOCATE:			SUB     '@'			; Check for valid range
			RET     C			; First character not "@", "A" to "Z" or "a" to "z", so not a variable
			LD      HL, 0			; Clear HL
			CP      'Z'-'@'+1		; Check for static ("@", "A" to "Z"); if it is not static...
			JR      NC,LOC0         	; Then branch here
			LD	L, A			; HL = A
			LD      A,(IY+1)        	; Check the 2nd character
			CP      '%'			; If not "%" then it is not static...
			JR      NZ,LOC1         	; Branch here
			LD      A,(IY+2)		; Check the 3rd character
			CP      '('			; If it is "(" (array) then it is not static...
			JR      Z,LOC1          	; Branch here
;
; At this point we're dealing with a static variable
;
			ADD     HL,HL			; HL: Variable index * 4
			ADD	HL,HL
			LD      DE,STAVAR       	; The static variable area in memory
			ADD     HL,DE			; HL: The address of the static variable
			INC     IY			; Skip the program pointer past the static variable name
			INC     IY	
			LD      D,4             	; Set the type to be integer
			XOR     A			; Set the Z flag
			RET
;
; At this point it's potentially a dynamic variable, just need to do a few more checks
;
LOC0:			CP      '_'-'@'			; Check the first character is in
			RET     C			; the range "_" to 
			CP      'z'-'@'+1		; "z" (lowercase characters only)
			CCF				; If it is not in range then
			DEC     A               	; Set NZ flag and
			RET     C			; Exit here
			SUB     3			; This brings it in the range of 27 upwards (need to confirm)
			LD	L, A			; HL = A
;
; Yes, it's definitely a dynamic variable at this point...
;
LOC1:			LD	A, L			; Fetch variable index
			ADD	A, A			; x 2
			ADD	A, L			; x 3
			SUB	3			; Subtract 2 TODO: Should be 3
			LD	L, A
			LD      DE, DYNVAR       	; The dynamic variable storage
			RET	C			; Bounds check to trap for variable '@'
			ADD     HL, DE			; HL: Address of first entry
;
; Loop through the linked list of variables to find a match
;
LOC2:			LD	DE, (HL)		; Fetch the original pointer
			PUSH	HL			; Need to preserve HL for LOC6
			XOR	A			; Reset carry flag
			SBC	HL, HL			; Set HL to 0
			SBC	HL, DE			; Compare with 0
			POP	HL			; Restore the original pointer
			JR	Z, LOC6			; If the pointer in DE is zero, the variable is undefined at this point
			; LD	HL, DE			; Make a copy of this pointer in HL
			push de ; HOW DID THE ABOVE EVEN ASSEMBLE IN THE ORIGINAL?!
			pop hl	; Make a copy of this pointer in HL
			INC     HL              	; Skip the link (24-bits)
			INC     HL
			INC	HL			; HL: Address of the variable name in DYNVARS
			PUSH    IY			; IY: Address of the variable name in the program
;
LOC3:			LD      A,(HL)         		; Compare
			INC     HL
			INC     IY
			CP      (IY)
			JR      Z, LOC3			; Keep looping whilst we've got a match...
			OR      A               	; Have we hit a terminator?
			JR      Z,LOC5          	; Yes, so maybe we've found a variable
;
LOC4:			POP     IY			; Restore the pointer in the program
			EX      DE, HL			; HL: New pointer in DYNVARS
			JP      LOC2            	; Loop round and try again
;
; We might have located a variable at this point, just need to do a few more tests
;
LOC5:			DEC     IY
			LD      A,(IY)
			CP      '('
			JR      Z,LOC5A         	; FOUND
			INC     IY
			CALL    RANGE
			JR      C,LOC5A         	; FOUND
			CP      '('
			JR      Z,LOC4          	; KEEP LOOKING
			LD      A,(IY-1)
			CALL    RANGE1
			JR      NC,LOC4         	; KEEP LOOKING
LOC5A:			POP     DE
TYPE_:			LD      A,(IY-1)		; Check the string type postfix
			CP      '$'			; Is it a string?
			LD      D,129			; Yes, so return D = 129
			RET     Z               		
			CP      '%'			; Is it an integer?
			LD      D,4			; Yes, so return D = 4
			RET     Z               		
			INC     D			; At this point it must be a float
			CP      A			; Set the flags
			RET
;
; The variable is undefined at this point; HL will be zero
;
LOC6:			INC     A               	; Set NZ flag
			RET
;
; from exec.asm

; 16-bit unsigned multiply
; - HL: Operand 1
; - BC: Operand 2
; Returns:
; - HL: Result
; -  F: C if overflow
;
MUL16:			PUSH	BC
			LD	D, C			; Set up the registers for the multiplies
			LD	E, L		
			LD	L, C
			LD	C, E
			MLT	HL			; HL = H * C (*256)
			MLT	DE			; DE = L * C
			MLT	BC			; BC = B * L (*256)
			ADD	HL, BC			; HL = The sum of the two most significant multiplications
			POP	BC
			XOR	A
			SBC	H			; If H is not zero then it's an overflow
			RET	C
			LD	H, L			; HL = ((H * C) + (B * L) * 256) + (L * C)
			LD	L, A
			ADD	HL, DE
			RET


; Multiply by 4 or 5
; This function is used to allocate space for dimensioned variables
; This is a 24-bit operation
; - DE: Number to multiple
; -  A: 04h (Integer) - takes up 4 bytes
;       05h (Float)   - takes up 5 bytes
;       81h (String)  - takes up 5 bytes - this is different from BBC BASIC for Z80 where strings only take up 4 bytes
; Returns:
; - DE: Multiplied by 4 if A = 4, otherwise multiplies by 5
; -  F: Carry if overflow
; Corrupts:
; - HL
X4OR5:			CP      4			; Check A = 4 (Z flag is used later)
			; LD	HL,DE  ; HOW!?
			push de
			pop hl
			ADD     HL,HL			; Multiply by 2 (note this operation preserves the zero flag)
			RET     C			; Exit if overflow
			ADD     HL,HL			; Multiply by 2 again
			RET     C			; Exit if overflow
			EX      DE,HL			; DE: Product
			RET     Z			; Exit if A = 4
			ADD     HL,DE			; Add original value to HL (effectively multiplying by 5)
			EX      DE,HL			; DE: Product
			RET


; from main.asm
; TEST FOR VALID CHARACTER IN VARIABLE NAME:
;   Inputs: IY addresses character
;  Outputs: Carry set if out-of-range.
; Destroys: A,F
;
; It is called here to check the following
; In range: "$", "%" and "("
;   Plus all characters in RANGE1 and RANGE2
;
RANGE:			LD      A,(IY)			; Fetch the character
			CP      '$'			; Postfix for string variable is valid
			RET     Z
			CP      '%'			; Postfix for integer variable is valid
			RET     Z
			CP      '('			; Postfix for array is valid
			RET     Z
;
; It is called here to check the following
; In range: "0" to "9" and "@"
;   Plus all characters in RANGE2
;
RANGE1:			CP      '0'			; If it is between '0'...
			RET     C			 
			CP      '9'+1			; And '9'...
			CCF
			RET     NC			; Then it is valid
			CP      '@'             	; The prefix @ is valid (@% controls numeric print formatting - v2.4)
			RET     Z
;
; It is called here to check the following
; In range: "A" to "Z", "a' to "z", "_" and "`"
;	
RANGE2:			CP      'A'			; If it is between 'A'...
			RET     C
			CP      'Z'+1			; And 'Z'...
			CCF
			RET     NC			; Then it is valid
			CP      '_'			; If it is underscore, grave, or between 'a'
			RET     C
			CP      'z'+1			; And 'z'
			CCF				; Then it is valid
			RET


; Throw a 'LINE space' error (line too long)
; This is called from LEXAN
;
SPACE_: 		XOR     A
			; CALL    EXTERR          	; "LINE space"
			; DB    	LINE_, 8, 0
;
; LEXAN - LEXICAL ANALYSIS.
;  Bit 0,C: 1=left, 0=right
;  Bit 2,C: 1=in BINARY
;  Bit 3,C: 1=in HEX
;  Bit 4,C: 1=accept line number
;  Bit 5,C: 1=in variable, FN, PROC
;  Bit 6,C: 1=in REM, DATA, *
;  Bit 7,C: 1=in quotes
;   Inputs: IY addresses source string
;           DE addresses destination string (must be page boundary)
;            C sets initial mode
;  Outputs: DE, IY updated
;            A holds carriage return
;
LEXAN1:			LD      (DE),A          	; Transfer to buffer
			INC     DE              	; Increment the pointers
			INC     IY			; And fall through to the main function
;
; This is the main entry point
;
LEXAN2:			LD      A,E             	; Destination buffer on page boundary, so E can be used as length
			CP      252             	; If it is >= 252 bytes, then...
			JR      NC,SPACE_        	; Throw a 'LINE space' error (line too long)
			LD      A,(IY)			; Fetch character from source string
			CP      CR			; If it is a CR
			RET     Z               	; Then it is end of line; we're done parsing
			CALL    RANGE1			; Is it alphanumeric, '@', '_' or '`'
			JR      NC,LEXAN3		; Yes, so skip
			RES     5,C             	; FLAG: NOT IN VARIABLE
			RES     3,C             	; FLAG: NOT IN HEX
			RES	2,C			; FLAG: NOT IN BINARY
;
LEXAN3:			CP      ' '			; Ignore spaces
			JR      Z,LEXAN1        	
			CP      ','			; Ignore commas
			JR      Z,LEXAN1 
			CP	'2'			; If less than '2'
			JR	NC, @F			; No, so skip
			RES	2,C			; FLAG: NOT IN BINARY
@@:			CP      'G'			; If less then 'G'
			JR      C,LEXAN4		; Yes, so skip
			RES     3,C             	; FLAG: NOT IN HEX
;
LEXAN4:			CP      34			; Is it a quote character?
			JR      NZ,LEXAN5		; No, so skip
			RL      C			; Toggle bit 7 of C by shifting it into carry flag
			CCF                     	; Toggle the carry
			RR      C			; And then shifting it back into bit 7 of C
;
LEXAN5:			
            ; BIT     4,C			; Accept line number?
			; JR      Z,LEXAN6		; No, so skip
			; RES     4,C			; FLAG: DON'T ACCEPT LINE NUMBER
			; PUSH    BC			
			; PUSH    DE
			; CALL    LINNUM         		; Parse the line number to HL
			; POP     DE
			; POP     BC
			; LD      A,H			; If it is not zero
			; OR      L
			; CALL    NZ,ENCODE       	; Then encode the line number HL to the destination (DE)
			; JR      LEXAN2          	; And loop
;
LEXAN6:			DEC     C			; Check for C=1 (LEFT)
			JR      Z,LEXAN7        	; If so, skip
			INC     C			; Otherwise restore C
			JR      NZ,LEXAN1		; If C was 0 (RIGHT) then...
			OR      A			; Set the flags based on the character
			CALL    P,LEX           	; Tokenise if A < 128
			JR      LEXAN8			; And skip
;
; Processing the LEFT hand side here
; 
LEXAN7:			CP      '*'			; Is it a '*' (for star commands)
			JR      Z,LEXAN9		; Yes, so skip to quit tokenising
			OR      A			; Set the flags based on the character
			CALL    P,LEX           	; Tokenise if A < 128
;
; This bit of code checks if the tokens are one of the pseudo-variables PTR, PAGE, TIME, LOMEM, HIMEM
; These tokens are duplicate in the table with a GET version and a SET version offset by the define OFFSET (40h)
; Examples:
;   LET A% = PAGE : REM This is the GET version
;   PAGE = 40000  : REM This is the SET version
;
			CP      TOKLO			; TOKLO is 8Fh
			JR      C,LEXAN8		; If A is < 8Fh then skip to LEX8
			CP      TOKHI+1			; TOKHI is 93h
			JR      NC,LEXAN8		; If A is >= 94h then skip to LEX8
			ADD     A,OFFSET       		; Add OFFSET (40h) to make the token the SET version
;
LEXAN8:			CP      REM			; If the token is REM
			JR      Z,LEXAN9		; Then stop tokenising
			CP      DATA_			; If it is not DATA then
			JR      NZ,LEXANA		; Skip
LEXAN9:			SET     6,C             	; FLAG: STOP TOKENISING
;
LEXANA:			CP      FN			; If the token is FN
			JR      Z,LEXANB		
			CP      PROC			; Or the token is PROC
			JR      Z,LEXANB		; Then jump to here
			CALL    RANGE2			; Otherwise check the input is alphanumeric, "_" or "`"
			JR      C,LEXANC		; Jump here if out of range
;
LEXANB:			SET     5,C             	; FLAG: IN VARIABLE/FN/PROC
LEXANC:			CP      '&'			; Check for hex prefix
			JR      NZ,LEXAND		; If not, skip
			SET     3,C             	; FLAG: IN HEX
;
LEXAND:			CP	'%'			; Check for binary prefix
			JR	NZ,LEXANE		; If not, skip
			SET	2,C			; FLAG: IN BINARY
;
LEXANE:			
            ; LD      HL,LIST1		; List of tokens that must be followed by a line number	
			; PUSH    BC			
			; LD      BC,LIST1L		; The list length
			; CPIR				; Check if the token is in this list
			; POP     BC
			; JR      NZ,LEXANF		; If not, then skip
			; SET     4,C             	; FLAG: ACCEPT LINE NUMBER
;
LEXANF:			
            ; LD      HL,LIST2		; List of tokens that switch the lexical analysis back to LEFT mode
			; PUSH    BC
			; LD      BC,LIST2L		; The list length
			; CPIR				; Check if the token is in this list
			; POP     BC		
			; JR      NZ,LEXANG		; If not, then skip
			; SET     0,C             	; FLAG: ENTER LEFT MODE
LEXANG:			JP      LEXAN1			; And loop


; SUBROUTINES:
;
; LEX - SEARCH FOR KEYWORDS
;   Inputs: HL = start of keyword table
;           IY = start of match text
;  Outputs: If found, Z-flag set, A=token.
;           If not found, Z-flag reset, A=(IY).
;           IY updated (if NZ, IY unchanged).
; Destroys: A,B,H,L,IY,F
;
LEX:			LD      HL,KEYWDS		; Address of the keywords table
;
LEX0:			LD      A,(IY)			; Fetch the character to match
			LD      B,(HL)			; B: The token from the keywords table
			INC     HL			; Increment the pointer in the keywords table
			CP      (HL)			; Compare the first characters
			JR      Z,LEX2			; If there is a match, then skip to LEX2
			RET     C               	; No match, so fail
;
; This snippet of code skips to the next token in the KEYWDS table
;
LEX1:			INC     HL			; Increment the pointer
			BIT     7,(HL)			; Check if bit 7 set (all token IDs have bit 7 set)
			JR      Z,LEX1			; No, so loop
			JR      LEX0			; At this point HL is pointing to the start of the next keyword
;
LEX2:			PUSH    IY              	; Save the input pointer
LEX3:			INC     HL			; Increment the keyword pointer
			BIT     7,(HL)			; If we've reached the end (marked by the start of the next token) then
			JR      NZ,LEX6         	; Jump to here as we've found a token
			INC     IY			; Increment the text pointer
			LD      A,(IY)			; Fetch the character
			CP      '.'			; Is it an abbreviated keyword?
			JR      Z,LEX6          	; Yes, so we'll return with the token we've found
			CP      (HL)			; Compare with the keywords list
			JR      Z,LEX3			; It's a match, so continue checking this keyword
			CALL    RANGE1			; Is it alphanumeric, '@', '_' or '`'
			JR      C,LEX5			; No, so check whether keyword needs to be immediately delimited
;	
LEX4:			POP     IY              	; Restore the input pointer ready for the next search
			JR      LEX1			; And loop back to start again
;
; This section handles the 0 byte at the end of keywords that indicate the keyword needs to be
; immediately delimited
;
LEX5:			LD      A,(HL)			; Fetch the byte from the keywords table	
			OR      A			; If it is not zero, then...
			JR      NZ,LEX4			; Keep searching
			DEC     IY			; If it is zero, then skip the input pointer back one byte
;
; We've found a token at this point
;
LEX6:			POP     AF			; Discard IY input pointer pushed on the stack
			XOR     A			; Set the Z flag
			LD      A,B			; A: The token
			RET


; A handful of common token IDs
;
TERROR:			EQU     85H
LINE_:			EQU     86H
ELSE_:			EQU     8BH
THEN:			EQU     8CH
LINO:			EQU     8DH
FN:			EQU     A4H
TO:			EQU     B8H
REN:			EQU     CCH
DATA_:			EQU     DCH
DIM:			EQU     DEH
FOR:			EQU     E3H
GOSUB:			EQU     E4H
GOTO:			EQU     E5H
TIF:			EQU     E7H
LOCAL_:			EQU     EAH
NEXT:			EQU     EDH
ON_:			EQU     EEH
PROC:			EQU     F2H
REM:			EQU     F4H
REPEAT:			EQU     F5H
RESTOR:			EQU     F7H
TRACE:			EQU     FCH
UNTIL:			EQU     FDH
;
; This defines the block of tokens that are pseudo-variables.
; There are two versions of each token, a GET and a SET

; Name  : GET : SET
; ------:-----:----
; PTR   : 8Fh : CFh 
; PAGE  : 90h : D0h
; TIME  : 91h : D1h
; LOMEM : 92h : D2h
; HIMEM : 93h : D3h
;
; Examples:
;   LET A% = PAGE : REM This is the GET version
;   PAGE = 40000  : REM This is the SET version
;
TOKLO:			EQU     8FH			; This defines the block of tokens that are pseudo-variables
TOKHI:			EQU     93H			; PTR, PAGE, TIME, LOMEM, HIMEM
OFFSET:			EQU     CFH-TOKLO		; Offset to the parameterised SET versions


; List of tokens and keywords. If a keyword is followed by 0 then
; it will only match with the keyword followed immediately by
; a delimiter
;
KEYWDS:			DB    80H, "AND"
			DB    94H, "ABS"
			DB    95H, "ACS"
			DB    96H, "ADVAL"
			DB    97H, "ASC"
			DB    98H, "ASN"
			DB    99H, "ATN"
			DB    C6H, "AUTO"
			DB    9AH, "BGET", 0
			DB    D5H, "BPUT", 0
			DB    FBH, "COLOUR"
			DB    FBH, "COLOR"
			DB    D6H, "CALL"
			DB    D7H, "CHAIN"
			DB    BDH, "CHR$"
			DB    D8H, "CLEAR", 0
			DB    D9H, "CLOSE", 0
			DB    DAH, "CLG", 0
			DB    DBH, "CLS", 0
			DB    9BH, "COS"
			DB    9CH, "COUNT", 0
			DB    DCH, "DATA"
			DB    9DH, "DEG"
			DB    DDH, "DEF"
			DB    C7H, "DELETE"
			DB    81H, "DIV"
			DB    DEH, "DIM"
			DB    DFH, "DRAW"
			DB    E1H, "ENDPROC", 0
			DB    E0H, "END", 0
			DB    E2H, "ENVELOPE"
			DB    8BH, "ELSE"
			DB    A0H, "EVAL"
			DB    9EH, "ERL", 0
			DB    85H, "ERROR"
			DB    C5H, "EOF", 0
			DB    82H, "EOR"
			DB    9FH, "ERR", 0
			DB    A1H, "EXP"
			DB    A2H, "EXT", 0
			DB    E3H, "FOR"
			DB    A3H, "FALSE", 0
			DB    A4H, "FN"
			DB    E5H, "GOTO"
			DB    BEH, "GET$"
			DB    A5H, "GET"
			DB    E4H, "GOSUB"
			DB    E6H, "GCOL"
			DB    93H, "HIMEM", 0
			DB    E8H, "INPUT"
			DB    E7H, "IF"
			DB    BFH, "INKEY$"
			DB    A6H, "INKEY"
			DB    A8H, "INT"
			DB    A7H, "INSTR("
			DB    C9H, "LIST"
			DB    86H, "LINE"
			DB    C8H, "LOAD"
			DB    92H, "LOMEM", 0
			DB    EAH, "LOCAL"
			DB    C0H, "LEFT$("
			DB    A9H, "LEN"
			DB    E9H, "LET"
			DB    ABH, "LOG"
			DB    AAH, "LN"
			DB    C1H, "MID$("
			DB    EBH, "MODE"
			DB    83H, "MOD"
			DB    ECH, "MOVE"
			DB    EDH, "NEXT"
			DB    CAH, "NEW", 0
			DB    ACH, "NOT"
			DB    CBH, "OLD", 0
			DB    EEH, "ON"
			DB    87H, "OFF"
			DB    84H, "OR"
			DB    8EH, "OPENIN"
			DB    AEH, "OPENOUT"
			DB    ADH, "OPENUP"
			DB    FFH, "OSCLI"
			DB    F1H, "PRINT"
			DB    90H, "PAGE", 0
			DB    8FH, "PTR", 0
			DB    AFH, "PI", 0
			DB    F0H, "PLOT"
			DB    B0H, "POINT("
			DB    F2H, "PROC"
			DB    B1H, "POS", 0
			DB    CEH, "PUT"
			DB    F8H, "RETURN", 0
			DB    F5H, "REPEAT"
			DB    F6H, "REPORT", 0
			DB    F3H, "READ"
			DB    F4H, "REM"
			DB    F9H, "RUN", 0
			DB    B2H, "RAD"
			DB    F7H, "RESTORE"
			DB    C2H, "RIGHT$("
			DB    B3H, "RND", 0
			DB    CCH, "RENUMBER"
			DB    88H, "STEP"
			DB    CDH, "SAVE"
			DB    B4H, "SGN"
			DB    B5H, "SIN"
			DB    B6H, "SQR"
			DB    89H, "SPC"
			DB    C3H, "STR$"
			DB    C4H, "STRING$("
			DB    D4H, "SOUND"
			DB    FAH, "STOP", 0
			DB    B7H, "TAN"
			DB    8CH, "THEN"
			DB    B8H, "TO"
			DB    8AH, "TAB("
			DB    FCH, "TRACE"
			DB    91H, "TIME", 0
			DB    B9H, "TRUE", 0
			DB    FDH, "UNTIL"
			DB    BAH, "USR"
			DB    EFH, "VDU"
			DB    BBH, "VAL"
			DB    BCH, "VPOS", 0
			DB    FEH, "WIDTH"
			DB    D3H, "HIMEM"
			DB    D2H, "LOMEM"
			DB    D0H, "PAGE"
			DB    CFH, "PTR"
			DB    D1H, "TIME"


; from exec.asm

; ASSIGN - Assign a numeric value to a variable.
; Outputs: NC,  Z - OK, numeric.
;          NC, NZ - OK, string.
;           C, NZ - illegal
;
ASSIGN:			CALL    GETVAR          	; Try to get the variable
			RET     C               	; Return with C if it is an illegal variable
			CALL    NZ,PUTVAR		; If it does not exist, then create the variable
			OR      A
			RET     M               	; Return if type is string (81h)
			PUSH    AF              	; It's a numeric type from this point on
			CALL    EQUALS			; Check if the variable is followed by an '=' symbol; this will throw a 'Mistake' error if not
			PUSH    HL
			CALL    EXPRN
			POP     IX
			POP     AF
STORE:			BIT     0,A
			JR      Z,STOREI
			CP      A               	; Set the variable to 0
STORE5:			LD      (IX+4),C
STORE4:			EXX
			LD      (IX+0),L
			LD      (IX+1),H
			EXX
			LD      (IX+2),L
			LD      (IX+3),H
			RET
STOREI:			PUSH    AF
			INC     C               ;SPEED - & PRESERVE F'
			DEC     C               ; WHEN CALLED BY FNEND0
			CALL    NZ,SFIX         ;CONVERT TO INTEGER
			POP     AF
			CP      4
			JR      Z,STORE4
			CP      A               ;SET ZERO
STORE1:			EXX
			LD      (IX+0),L
			EXX
			RET


; This snippet is used to check whether an expression is followed by an '=' symbol
;
EQUALS:			CALL    NXT			; Skip whitespace
			INC     IY			; Skip past the character in question
			CP      '='			; Is it '='
			RET     Z			; Yes, so return
			; LD      A,4			; Otherwise
			; JP      ERROR_           	; Throw error "Mistake"