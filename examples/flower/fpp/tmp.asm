; DIVA, DIVB - DIVISION PRIMITIVE.
;     Function: D'E'DE = H'L'HLD'E'DE / B'C'BC
;               Remainder in H'L'HL
;     Inputs: A = loop counter (normally -32)
;     Destroys: A,D,E,H,L,D',E',H',L',F
;
DIVA:			OR      A               ;CLEAR CARRY
DIV0:			
			SBC.S   HL,BC           ;DIVIDEND-DIVISOR
        		EXX
        		SBC.S   HL,BC
        		EXX
        		JR      NC,DIV1
        		ADD.S   HL,BC           ;DIVIDEND+DIVISOR
        		EXX
        		ADC.S   HL,BC
        		EXX
DIV1:			CCF
DIVC:			RL      E               ;SHIFT RESULT INTO DE
        		RL      D
        		EXX
        		RL      E
        		RL      D
        		EXX
        		INC     A
        		RET     P
DIVB:			
			ADC.S   HL,HL           ;DIVIDEND*2
        		EXX
        		ADC.S   HL,HL
        		EXX
        		JR      NC,DIV0
        		OR      A
        		SBC.S   HL,BC           ;DIVIDEND-DIVISOR
        		EXX
        		SBC.S   HL,BC
        		EXX
        		SCF
        		JP      DIVC
;
;MULA, MULB - MULTIPLICATION PRIMITIVE.
;    Function: H'L'HLD'E'DE = B'C'BC * D'E'DE
;    Inputs: A = loop counter (usually -32)
;            H'L'HL = 0
;    Destroys: D,E,H,L,D',E',H',L',A,F
;
MULA:			OR      A               ;CLEAR CARRY
MUL0:			EXX
        		RR      D               ;MULTIPLIER/2
        		RR      E
        		EXX
        		RR      D
        		RR      E
        		JR      NC,MUL1
        		ADD.S   HL,BC           ;ADD IN MULTIPLICAND
        		EXX
        		ADC.S   HL,BC
        		EXX
MUL1:			INC     A
        		RET     P
MULB:			EXX
        		RR      H               ;PRODUCT/2
        		RR      L
        		EXX
        		RR      H
        		RR      L
        		JP      MUL0