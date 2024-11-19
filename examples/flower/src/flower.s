; ==============================================================================
; from mos_api.inc
; ------------------------------------------------------------------------------
;
; Title:	AGON MOS - API for user projects
; Author:	Dean Belfield
; Created:	03/08/2022
; Last Updated:	11/11/2023
;
; Modinfo:
; 05/08/2022:	Added mos_feof
; 09/08/2022:	Added system variables: cursorX, cursorY
; 18/08/2022:	Added system variables: scrchar, scrpixel, audioChannel, audioSuccess, vpd_pflags
; 05/09/2022:	Added mos_ren, vdp_pflag_mode
; 24/09/2022:	Added mos_getError, mos_mkdir
; 13/10/2022:	Added mos_oscli
; 23/02/2023:	Added more sysvars, fixed typo in sysvar_audioSuccess, offsets for sysvar_scrCols, sysvar_scrRows
; 04/03/2023:	Added sysvar_scrpixelIndex
; 08/03/2023:	Renamed sysvar_keycode to sysvar_keyascii, added sysvar_vkeycode
; 15/03/2023:	Added mos_copy, mos_getrtc, mos_setrtc, rtc, vdp_pflag_rtc
; 21/03/2023:	Added mos_setintvector, sysvars for keyboard status, vdu codes for vdp
; 22/03/2023:	The VDP commands are now indexed from 0x80
; 29/03/2023:	Added mos_uopen, mos_uclose, mos_ugetc, mos_uputc
; 13/04/2023:	Added FatFS file structures (FFOBJID, FIL, DIR, FILINFO)
; 15/04/2023:	Added mos_getfil, mos_fread, mos_fwrite and mos_flseek
; 19/05/2023:	Added sysvar_scrMode
; 05/06/2023:	Added sysvar_rtcEnable
; 03/08/2023:	Added mos_setkbvector
; 10/08/2023:	Added mos_getkbmap
; 11/11/2023:	Added mos_i2c_open, mos_i2c_close, mos_i2c_write and mos_i2c_read

; VDP control (VDU 23, 0, n)
;
vdp_gp:			EQU 	80h
vdp_keycode:		EQU 	81h
vdp_cursor:		EQU	82h
vdp_scrchar:		EQU	83h
vdp_scrpixel:		EQU	84h
vdp_audio:		EQU	85h
vdp_mode:		EQU	86h
vdp_rtc:		EQU	87h
vdp_keystate:		EQU	88h
vdp_logicalcoords:	EQU	C0h
vdp_terminalmode:	EQU	FFh

; MOS high level functions
;
mos_getkey:		EQU	00h
mos_load:		EQU	01h
mos_save:		EQU	02h
mos_cd:			EQU	03h
mos_dir:		EQU	04h
mos_del:		EQU	05h
mos_ren:		EQU	06h
mos_mkdir:		EQU	07h
mos_sysvars:		EQU	08h
mos_editline:		EQU	09h
mos_fopen:		EQU	0Ah
mos_fclose:		EQU	0Bh
mos_fgetc:		EQU	0Ch
mos_fputc:		EQU	0Dh
mos_feof:		EQU	0Eh
mos_getError:		EQU	0Fh
mos_oscli:		EQU	10h
mos_copy:		EQU	11h
mos_getrtc:		EQU	12h
mos_setrtc:		EQU	13h
mos_setintvector:	EQU	14h
mos_uopen:		EQU	15h
mos_uclose:		EQU	16h
mos_ugetc:		EQU	17h
mos_uputc:		EQU 	18h
mos_getfil:		EQU	19h
mos_fread:		EQU	1Ah
mos_fwrite:		EQU	1Bh
mos_flseek:		EQU	1Ch
mos_setkbvector:	EQU	1Dh
mos_getkbmap:		EQU	1Eh
mos_i2c_open:		EQU	1Fh
mos_i2c_close:		EQU	20h
mos_i2c_write:		EQU	21h
mos_i2c_read:		EQU	22h


; FatFS file access functions
;
ffs_fopen:		EQU	80h
ffs_fclose:		EQU	81h
ffs_fread:		EQU	82h
ffs_fwrite:		EQU	83h
ffs_flseek:		EQU	84h
ffs_ftruncate:		EQU	85h
ffs_fsync:		EQU	86h
ffs_fforward:		EQU	87h
ffs_fexpand:		EQU	88h
ffs_fgets:		EQU	89h
ffs_fputc:		EQU	8Ah
ffs_fputs:		EQU	8Bh
ffs_fprintf:		EQU	8Ch
ffs_ftell:		EQU	8Dh
ffs_feof:		EQU	8Eh
ffs_fsize:		EQU	8Fh
ffs_ferror:		EQU	90h

; FatFS directory access functions
;
ffs_dopen:		EQU	91h
ffs_dclose:		EQU	92h
ffs_dread:		EQU	93h
ffs_dfindfirst:		EQU	94h
ffs_dfindnext:		EQU	95h

; FatFS file and directory management functions
;
ffs_stat:		EQU	96h
ffs_unlink:		EQU	97h
ffs_rename:		EQU	98h
ffs_chmod:		EQU	99h
ffs_utime:		EQU	9Ah
ffs_mkdir:		EQU	9Bh
ffs_chdir:		EQU	9Ch
ffs_chdrive:		EQU	9Dh
ffs_getcwd:		EQU	9Eh

; FatFS volume management and system configuration functions
;
ffs_mount:		EQU	9Fh
ffs_mkfs:		EQU	A0h
ffs_fdisk:		EQU	A1h
ffs_getfree:		EQU	A2h
ffs_getlabel:		EQU	A3h
ffs_setlabel:		EQU	A4h
ffs_setcp:		EQU	A5h
	
; File access modes
;
fa_read:		EQU	01h
fa_write:		EQU	02h
fa_open_existing:	EQU	00h
fa_create_new:		EQU	04h
fa_create_always:	EQU	08h
fa_open_always:		EQU	10h
fa_open_append:		EQU	30h
	
; System variable indexes for api_sysvars
; Index into _sysvars in globals.asm
;
sysvar_time:		EQU	00h	; 4: Clock timer in centiseconds (incremented by 2 every VBLANK)
sysvar_vpd_pflags:	EQU	04h	; 1: Flags to indicate completion of VDP commands
sysvar_keyascii:	EQU	05h	; 1: ASCII keycode, or 0 if no key is pressed
sysvar_keymods:		EQU	06h	; 1: Keycode modifiers
sysvar_cursorX:		EQU	07h	; 1: Cursor X position
sysvar_cursorY:		EQU	08h	; 1: Cursor Y position
sysvar_scrchar:		EQU	09h	; 1: Character read from screen
sysvar_scrpixel:	EQU	0Ah	; 3: Pixel data read from screen (R,B,G)
sysvar_audioChannel:	EQU	0Dh	; 1: Audio channel 
sysvar_audioSuccess:	EQU	0Eh	; 1: Audio channel note queued (0 = no, 1 = yes)
sysvar_scrWidth:	EQU	0Fh	; 2: Screen width in pixels
sysvar_scrHeight:	EQU	11h	; 2: Screen height in pixels
sysvar_scrCols:		EQU	13h	; 1: Screen columns in characters
sysvar_scrRows:		EQU	14h	; 1: Screen rows in characters
sysvar_scrColours:	EQU	15h	; 1: Number of colours displayed
sysvar_scrpixelIndex:	EQU	16h	; 1: Index of pixel data read from screen
sysvar_vkeycode:	EQU	17h	; 1: Virtual key code from FabGL
sysvar_vkeydown:	EQU	18h	; 1: Virtual key state from FabGL (0=up, 1=down)
sysvar_vkeycount:	EQU	19h	; 1: Incremented every time a key packet is received
sysvar_rtc:		EQU	1Ah	; 6: Real time clock data
sysvar_spare:		EQU	20h	; 2: Spare, previously used by rtc
sysvar_keydelay:	EQU	22h	; 2: Keyboard repeat delay
sysvar_keyrate:		EQU	24h	; 2: Keyboard repeat reat
sysvar_keyled:		EQU	26h	; 1: Keyboard LED status
sysvar_scrMode:		EQU	27h	; 1: Screen mode
sysvar_rtcEnable:	EQU	28h	; 1: RTC enable flag (0: disabled, 1: use ESP32 RTC)
sysvar_mouseX:		EQU	29h	; 2: Mouse X position
sysvar_mouseY:		EQU	2Bh	; 2: Mouse Y position
sysvar_mouseButtons:	EQU	2Dh	; 1: Mouse button state
sysvar_mouseWheel:	EQU	2Eh	; 1: Mouse wheel delta
sysvar_mouseXDelta:	EQU	2Fh	; 2: Mouse X delta
sysvar_mouseYDelta:	EQU	31h	; 2: Mouse Y delta
	
; Flags for the VPD protocol
;
vdp_pflag_cursor:	EQU	00000001b
vdp_pflag_scrchar:	EQU	00000010b
vdp_pflag_point:	EQU	00000100b
vdp_pflag_audio:	EQU	00001000b
vdp_pflag_mode:		EQU	00010000b
vdp_pflag_rtc:		EQU	00100000b
vdp_pflag_mouse:	EQU	01000000b
; vdp_pflag_buffered:	EQU	10000000b

; FFOBJID offsets
FFOBJID.fs:       EQU 0    ; Pointer to the hosting volume of this object
FFOBJID.id:       EQU 3    ; Hosting volume mount ID
FFOBJID.attr:     EQU 5    ; Object attribute
FFOBJID.stat:     EQU 6    ; Object chain status
FFOBJID.sclust:   EQU 7    ; Object data start cluster
FFOBJID.objsize:  EQU 11   ; Object size
FFOBJID_SIZE:     EQU 15   ; Total size of FFOBJID structure

; FIL offsets (including FFOBJID fields)
FIL.obj:          EQU 0                  ; Object identifier (FFOBJID fields start here)
FIL.flag:         EQU FFOBJID_SIZE       ; File status flags
FIL.err:          EQU FFOBJID_SIZE + 1   ; Abort flag (error code)
FIL.fptr:         EQU FFOBJID_SIZE + 2   ; File read/write pointer
FIL.clust:        EQU FFOBJID_SIZE + 6   ; Current cluster of fptr
FIL.sect:         EQU FFOBJID_SIZE + 10  ; Sector number appearing in buf[]
FIL.dir_sect:     EQU FFOBJID_SIZE + 14  ; Sector number containing the directory entry
FIL.dir_ptr:      EQU FFOBJID_SIZE + 18  ; Pointer to the directory entry in the win[]
FIL_SIZE:         EQU FFOBJID_SIZE + 21  ; Total size of FIL structure

; DIR offsets (including FFOBJID fields)
DIR.obj:          EQU 0                  ; Object identifier (FFOBJID fields start here)
DIR.dptr:         EQU FFOBJID_SIZE       ; Current read/write offset
DIR.clust:        EQU FFOBJID_SIZE + 4   ; Current cluster
DIR.sect:         EQU FFOBJID_SIZE + 8   ; Current sector
DIR.dir:          EQU FFOBJID_SIZE + 12  ; Pointer to the directory item in the win[]
DIR.fn:           EQU FFOBJID_SIZE + 15  ; SFN (in/out) {body[8],ext[3],status[1]}
DIR.blk_ofs:      EQU FFOBJID_SIZE + 27  ; Offset of current entry block being processed
DIR_SIZE:         EQU FFOBJID_SIZE + 31  ; Total size of DIR structure

; FILINFO offsets
FILINFO.fsize:    EQU 0    ; File size
FILINFO.fdate:    EQU 4    ; Modified date
FILINFO.ftime:    EQU 6    ; Modified time
FILINFO.fattrib:  EQU 8    ; File attribute
FILINFO.altname:  EQU 9    ; Alternative file name
FILINFO.fname:    EQU 22   ; Primary file name
FILINFO_SIZE:     EQU 278  ; Total size of FILINFO structure

;
; Macro for calling the API
; Parameters:
; - function: One of the function numbers listed above
;
			MACRO MOSCALL	function
			LD	A, function
			RST.LIS	08h
			ENDMACRO 	

; ==============================================================================
; from basic/fpp.asm
; ------------------------------------------------------------------------------

;
; Title:	BBC Basic Interpreter - Z80 version
;		Z80 Floating Point Package
; Author:	(C) Copyright  R.T.Russell  1986
; Modified By:	Dean Belfield
; Created:	03/05/2022
; Last Updated:	07/06/2023
;
; Modinfo:
; 26/10/1986:	Version 0.0
; 14/12/1988:	Vesion 0.1 (Bug Fix)
; 12/05/2023:	Modified by Dean Belfield
; 07/06/2023:	Modified to run in ADL mode

			; .ASSUME	ADL = 1

			; SEGMENT CODE
				
			; XDEF	FPP
			; XDEF	DLOAD5
			; XDEF	DLOAD5_SPL			
;
;BINARY FLOATING POINT REPRESENTATION:
;   32 BIT SIGN-MAGNITUDE NORMALIZED MANTISSA
;    8 BIT EXCESS-128 SIGNED EXPONENT
;   SIGN BIT REPLACES MANTISSA MSB (IMPLIED "1")
;   MANTISSA=0 & EXPONENT=0 IMPLIES VALUE IS ZERO.
;
;BINARY INTEGER REPRESENTATION:
;   32 BIT 2'S-COMPLEMENT SIGNED INTEGER
;    "EXPONENT" BYTE = 0 (WHEN PRESENT)
;
;NORMAL REGISTER ALLOCATION: MANTISSA - HLH'L'
;                            EXPONENT - C
;ALTERNATE REGISTER ALLOCATION: MANTISSA - DED'E'
;                               EXPONENT - B

;
;Error codes:
;

BADOP:			EQU     1               ;Bad operation code
DIVBY0:			EQU     18              ;Division by zero
TOOBIG_FP:			EQU     20              ;Too big
NGROOT:			EQU     21              ;Negative root
LOGRNG:			EQU     22              ;Log range
ACLOST:			EQU     23              ;Accuracy lost
EXPRNG:			EQU     24              ;Exp range
;
;Call entry and despatch code:
;
FPP:			PUSH    IY              ;Save IY
        		LD      IY,0
        		ADD     IY,SP           ;Save SP in IY
        		CALL    OP              ;Perform operation
        		CP      A               ;Good return (Z, NC)
EXIT_FP_:			POP     IY              ;Restore IY
        		RET                     ;Return to caller
;
;Error exit:
;
BAD_FP:			LD      A,BADOP         ;"Bad operation code"
ERROR_FP_:			LD      SP,IY           ;Restore SP from IY
        		OR      A               ;Set NZ
        		SCF                     ;Set C
        		JR      EXIT_FP_
;
;Perform operation or function:
;
; OP:			CP      (RTABLE-DTABLE)/3
OP:				CP      RTABLE-DTABLE/3 ; ez80asm doesn't do nested expressions

        		JR      NC,BAD_FP
        		; CP      (FTABLE-DTABLE)/3
				CP      FTABLE-DTABLE/3 ; ditto
        		JR      NC,DISPAT_FP
        		EX      AF,AF'
        		LD      A,B
        		OR      C               ;Both integer?
        		CALL    NZ,FLOATA       ;No, so float both
        		EX      AF,AF'
DISPAT_FP:			PUSH    HL
        		LD      HL,DTABLE
        		PUSH    BC
			LD	BC, 3		; C = 3
			LD	B, A 		; B = op-code
			MLT 	BC 		;BC = op-code * 3
			ADD	HL, BC 		;Add to table base 
			LD	HL, (HL)	;Get the routine address (24-bit)

;        		ADD     A, A            ;A = op-code * 2
;        		LD      C,A
;        		LD      B,0             ;BC = op-code * 2
;        		ADD     HL,BC
;        		LD      A,(HL)          ;Get low byte
;        		INC     HL
;        		LD      H,(HL)          ;Get high byte
;        		LD      L,A

        		POP     BC
        		EX      (SP),HL
        		RET                     ;Off to routine
;
;Despatch table:
;
DTABLE:			DW24  IAND            ;AND (INTEGER)
        		DW24  IBDIV           ;DIV
        		DW24  IEOR            ;EOR
        		DW24  IMOD            ;MOD
        		DW24  IOR             ;OR
        		DW24  ILE             ;<=
        		DW24  INE             ;<>
        		DW24  IGE             ;>=
        		DW24  ILT             ;<
        		DW24  IEQ             ;=
        		DW24  IMUL            ;*
        		DW24  IADD            ;+
        		DW24  IGT             ;>
        		DW24  ISUB            ;-
        		DW24  IPOW            ;^
        		DW24  IDIV            ;/
;
FTABLE:			
				DW24  ABSV_FP            ;ABS
        		DW24  ACS_FP             ;ACS
        		DW24  ASN_FP             ;ASN
        		DW24  ATN_FP             ;ATN
        		DW24  COS_FP             ;COS
        		DW24  DEG_FP             ;DEG
        		DW24  EXP_FP             ;EXP
        		DW24  INT_FP_            ;INT
        		DW24  LN_FP              ;LN
        		DW24  LOG_FP             ;LOG
        		DW24  NOTK_FP            ;NOT
        		DW24  RAD_FP             ;RAD
        		DW24  SGN_FP             ;SGN
        		DW24  SIN_FP             ;SIN
        		DW24  SQR_FP             ;SQR
        		DW24  TAN_FP             ;TAN
;
		        DW24  ZERO_FP            ;ZERO
        		DW24  FONE_FP            ;FONE
        		DW24  TRUE_FP            ;TRUE
        		DW24  PI_FP              ;PI
;
		        DW24  VAL_FP             ;VAL
        		DW24  STR_FP             ;STR$
;
        		DW24  SFIX_FP            ;FIX
        		DW24  SFLOAT_FP          ;FLOAT
;
		        DW24  FTEST_FP           ;TEST
        		DW24  FCOMP_FP           ;COMPARE
;
RTABLE:			DW24  FAND            ;AND (FLOATING-POINT)
        		DW24  FBDIV           ;DIV
        		DW24  FEOR            ;EOR
        		DW24  FMOD            ;MOD
        		DW24  FFOR             ;OR
        		DW24  FLE             ;<= 
        		DW24  FNE             ;<>
        		DW24  FGE             ;>=
        		DW24  FLT             ;<
        		DW24  FEQ             ;=
        		DW24  FMUL            ;*
        		DW24  FADD            ;+
        		DW24  FGT             ;>
        		DW24  FSUB            ;-
        		DW24  FPOW            ;^
        		DW24  FDIV            ;/
;
;       PAGE
;
;ARITHMETIC AND LOGICAL OPERATORS:
;All take two arguments, in HLH'L'C & DED'E'B.
;Output in HLH'L'C
;All registers except IX, IY destroyed.
; (N.B. FPOW destroys IX).
;
;FAND - Floating-point AND.
;IAND - Integer AND.
;
FAND:			CALL    FIX2
IAND:			LD      A,H
        		AND     D
        		LD      H,A
        		LD      A,L
        		AND     E
        		LD      L,A
        		EXX
        		LD      A,H
        		AND     D
        		LD      H,A
        		LD      A,L
        		AND     E
        		LD      L,A
        		EXX
        		RET
;
;FEOR - Floating-point exclusive-OR.
;IEOR - Integer exclusive-OR.
;
FEOR:			CALL    FIX2
IEOR:			LD      A,H
        		XOR     D
        		LD      H,A
        		LD      A,L
        		XOR     E
        		LD      L,A
        		EXX
        		LD      A,H
        		XOR     D
        		LD      H,A
        		LD      A,L
        		XOR     E
        		LD      L,A
        		EXX
        		RET
;
;FOR - Floating-point OR.
;IOR - Integer OR.
;
FFOR:			CALL    FIX2
IOR:			LD      A,H
        		OR      D
        		LD      H,A
        		LD      A,L
        		OR      E
        		LD      L,A
        		EXX
        		LD      A,H
        		OR      D
        		LD      H,A
        		LD      A,L
        		OR      E
        		LD      L,A
        		EXX
        		RET
;
;FMOD - Floating-point remainder.
;IMOD - Integer remainder.
;
FMOD:			CALL    FIX2
IMOD:			LD      A,H
        		XOR     D               ;DIV RESULT SIGN
        		BIT     7,H
        		EX      AF,AF'
        		BIT     7,H
        		CALL    NZ,NEGATE       ;MAKE ARGUMENTS +VE
        		CALL    SWAP_FP
        		BIT     7,H
        		CALL    NZ,NEGATE
        		LD      B,H
        		LD      C,L
        		LD      HL,0
        		EXX
        		LD      B,H
        		LD      C,L
        		LD      HL,0
        		LD      A,-33
        		CALL    DIVA            ;DIVIDE
        		EXX
        		LD      C,0             ;INTEGER MARKER
        		EX      AF,AF'
        		RET     Z
        		JP      NEGATE
;
;BDIV - Integer division.
;
FBDIV:			CALL    FIX2
IBDIV:			CALL    IMOD
        		OR      A
        		CALL    SWAP_FP
        		LD      C,0
        		RET     P
        		JP      NEGATE
;
;ISUB - Integer subtraction.
;FSUB - Floating point subtraction with rounding.
;
ISUB:			CALL    SUB_
        		RET     PO
        		CALL    ADD_
        		CALL    FLOAT2
FSUB:			LD      A,D
        		XOR     80H             ;CHANGE SIGN THEN ADD
        		LD      D,A
        		JR      FADD
;
;Reverse subtract.
;
RSUB:			LD      A,H
        		XOR     80H
        		LD      H,A
        		JR      FADD
;
;IADD - Integer addition.
;FADD - Floating point addition with rounding.
;
IADD:			CALL    ADD_
        		RET     PO
        		CALL    SUB_
        		CALL    FLOAT2
FADD:			DEC     B
        		INC     B
        		RET     Z               ;ARG 2 ZERO
        		DEC     C
        		INC     C
        		JP      Z,SWAP_FP          ;ARG 1 ZERO
        		EXX
        		LD      BC,0            ;INITIALISE
        		EXX
        		LD      A,H
        		XOR     D               ;XOR SIGNS
        		PUSH    AF
        		LD      A,B
        		CP      C               ;COMPARE EXPONENTS
        		CALL    C,SWAP_FP          ;MAKE DED'E'B LARGEST
        		LD      A,B
        		SET     7,H             ;IMPLIED 1
        		CALL    NZ,FIX          ;ALIGN
        		POP     AF
        		LD      A,D             ;SIGN OF LARGER
        		SET     7,D             ;IMPLIED 1
        		JP      M,FADD3         ;SIGNS DIFFERENT
        		CALL    ADD_             ;HLH'L'=HLH'L'+DED'E'
        		CALL    C,DIV2          ;NORMALISE
        		SET     7,H
        		JR      FADD4
;
FADD3:			CALL    SUB_             ;HLH'L'=HLH'L'-DED'E'
        		CALL    C,NEG_           ;NEGATE HLH'L'B'C'
        		CALL    FLO48
        		CPL                     ;CHANGE RESULT SIGN
FADD4:			EXX
        		EX      DE,HL
        		LD      HL,8000H
        		OR      A               ;CLEAR CARRY
        		SBC.S   HL,BC
        		EX      DE,HL
        		EXX
        		CALL    Z,ODD           ;ROUND UNBIASSED
        		CALL    C,ADD1_FP          ;ROUND UP
        		CALL    C,INCC
        		RES     7,H
        		DEC     C
        		INC     C
        		JP      Z,ZERO_FP
        		OR      A               ;RESULT SIGNQ
        		RET     P               ;POSITIVE
        		SET     7,H             ;NEGATIVE
        		RET
;
;IDIV - Integer division.
;FDIV - Floating point division with rounding.
;
IDIV:			CALL    FLOAT2
FDIV:			DEC     B               ;TEST FOR ZERO
        		INC     B
        		LD      A,DIVBY0
        		JP      Z,ERROR_FP_         ;"Division by zero"
        		DEC     C               ;TEST FOR ZERO
        		INC     C
        		RET     Z
        		LD      A,H
        		XOR     D               ;CALC. RESULT SIGN
        		EX      AF,AF'          ;SAVE SIGN
        		SET     7,D             ;REPLACE IMPLIED 1's
        		SET     7,H
        		PUSH    BC              ;SAVE EXPONENTS
        		LD      B,D             ;LOAD REGISTERS
        		LD      C,E
        		LD      DE,0
        		EXX
        		LD      B,D
        		LD      C,E
        		LD      DE,0
        		LD      A,-32           ;LOOP COUNTER
        		CALL    DIVA            ;DIVIDE
        		EXX
        		BIT     7,D
        		EXX
        		CALL    Z,DIVB          ;NORMALISE & INC A
        		EX      DE,HL
        		EXX
        		SRL     B               ;DIVISOR/2
        		RR      C
        		OR      A               ;CLEAR CARRY
        		SBC.S   HL,BC           ;REMAINDER-DIVISOR/2
        		CCF
        		EX      DE,HL           ;RESULT IN HLH'L'
        		CALL    Z,ODD           ;ROUND UNBIASSED
        		CALL    C,ADD1_FP          ;ROUND UP
        		POP     BC              ;RESTORE EXPONENTS
        		CALL    C,INCC
        		RRA                     ;LSB OF A TO CARRY
        		LD      A,C             ;COMPUTE NEW EXPONENT
        		SBC     A,B
        		CCF
        		JP      CHKOVF
;
;IMUL - Integer multiplication.
;
IMUL:			LD      A,H
        		XOR     D
        		EX      AF,AF'          ;SAVE RESULT SIGN
        		BIT     7,H
        		CALL    NZ,NEGATE
        		CALL    SWAP_FP
        		BIT     7,H
        		CALL    NZ,NEGATE
        		LD      B,H
        		LD      C,L
        		LD      HL,0
        		EXX
        		LD      B,H
        		LD      C,L
        		LD      HL,0
        		LD      A,-33
        		CALL    MULA            ;MULTIPLY
        		EXX
        		LD      C,191           ;PRESET EXPONENT
        		CALL    TEST_FP            ;TEST RANGE
        		JR      NZ,IMUL1        ;TOO BIG
        		BIT     7,D
        		JR      NZ,IMUL1
        		CALL    SWAP_FP
        		LD      C,D             ;INTEGER MARKER
        		EX      AF,AF'
        		RET     P
        		JP      NEGATE
;
IMUL1:			DEC     C
        		EXX
        		SLA     E
        		RL      D
        		EXX
        		RL      E
        		RL      D
        		EXX
        		ADC.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		JP      P,IMUL1         ;NORMALISE
        		EX      AF,AF'
        		RET     M
        		RES     7,H             ;POSITIVE
        		RET
;
;FMUL - Floating point multiplication with rounding.
;
FMUL:			DEC     B               ;TEST FOR ZERO
        		INC     B
        		JP      Z,ZERO_FP
        		DEC     C               ;TEST FOR ZERO
        		INC     C
        		RET     Z
        		LD      A,H
        		XOR     D               ;CALC. RESULT SIGN
        		EX      AF,AF'
        		SET     7,D             ;REPLACE IMPLIED 1's
        		SET     7,H
        		PUSH    BC              ;SAVE EXPONENTS
        		LD      B,H             ;LOAD REGISTERS
        		LD      C,L
        		LD      HL,0
        		EXX
        		LD      B,H
        		LD      C,L
        		LD      HL,0
        		LD      A,-32           ;LOOP COUNTER
        		CALL    MULA            ;MULTIPLY
        		CALL    C,MULB          ;NORMALISE & INC A
        		EXX
        		PUSH    HL
        		LD      HL,8000H
        		OR      A               ;CLEAR CARRY
        		SBC.S   HL,DE
        		POP     HL
        		CALL    Z,ODD           ;ROUND UNBIASSED
        		CALL    C,ADD1_FP          ;ROUND UP
        		POP     BC              ;RESTORE EXPONENTS
        		CALL    C,INCC
        		RRA                     ;LSB OF A TO CARRY
        		LD      A,C             ;COMPUTE NEW EXPONENT
        		ADC     A,B
CHKOVF:			JR      C,CHKO1
        		JP      P,ZERO_FP          ;UNDERFLOW
        		JR      CHKO2
CHKO1:			JP      M,OFLOW         ;OVERFLOW
CHKO2:			ADD     A,80H
        		LD      C,A
        		JP      Z,ZERO_FP
        		EX      AF,AF'          ;RESTORE SIGN BIT
        		RES     7,H
        		RET     P
        		SET     7,H
        		RET
;
;IPOW - Integer involution.
;
IPOW:			CALL    SWAP_FP
        		BIT     7,H
        		PUSH    AF              ;SAVE SIGN
        		CALL    NZ,NEGATE
IPOW0:			LD      C,B
        		LD      B,32            ;LOOP COUNTER
IPOW1:			CALL    X2
        		JR      C,IPOW2
        		DJNZ    IPOW1
        		POP     AF
        		EXX
        		INC     L               ;RESULT=1
        		EXX
        		LD      C,H
        		RET
;
IPOW2:			POP     AF
        		PUSH    BC
        		EX      DE,HL
        		PUSH    HL
        		EXX
        		EX      DE,HL
        		PUSH    HL
        		EXX
        		LD      IX,0
        		ADD     IX,SP
        		JR      Z,IPOW4
        		PUSH    BC
        		EXX
        		PUSH    DE
        		EXX
        		PUSH    DE
        		CALL    SFLOAT_FP
        		CALL    RECIP
        		LD      (IX+4),C
        		EXX
        		LD      (IX+0),L
        		LD      (IX+1),H
        		EXX
        		LD      (IX+2),L
        		LD      (IX+3),H
        		JR      IPOW5
;
IPOW3:			PUSH    BC
        		EXX
        		SLA     E
        		RL      D
        		PUSH    DE
        		EXX
        		RL      E
        		RL      D
        		PUSH    DE
        		LD      A,'*' & 0FH
        		PUSH    AF
        		CALL    COPY_
        		CALL    OP              ;SQUARE
        		POP     AF
        		CALL    DLOAD5
        		CALL    C,OP            ;MULTIPLY BY X
IPOW5:			POP     DE
        		EXX
        		POP     DE
        		EXX
        		LD      A,C
        		POP     BC
        		LD      C,A
IPOW4:			DJNZ    IPOW3
        		POP     AF
        		POP     AF
        		POP     AF
        		RET
;
FPOW0:			POP     AF
        		POP     AF
        		POP     AF
        		JR      IPOW0
;
;FPOW - Floating-point involution.
;
FPOW:			BIT     7,D
        		PUSH    AF
        		CALL    SWAP_FP
        		CALL    PUSH5
        		DEC     C
        		INC     C
        		JR      Z,FPOW0
        		LD      A,158
        		CP      C
        		JR      C,FPOW1
        		INC     A
        		CALL    FIX
        		EX      AF,AF'
        		JP      P,FPOW0
FPOW1:			CALL    SWAP_FP
        		CALL    LN0
        		CALL    POP5
        		POP     AF
        		CALL    FMUL
        		JP      EXP0
;
;Integer and floating-point compare.
;Result is TRUE (-1) or FALSE (0).
;
FLT:			CALL    FCP
        		JR      ILT1
ILT:			CALL    ICP
ILT1:			RET     NC
        		JR      TRUE_FP
;
FGT:			CALL    FCP
        		JR      IGT1
IGT:			CALL    ICP
IGT1:			RET     Z
        		RET     C
        		JR      TRUE_FP
;
FGE:			CALL    FCP
        		JR      IGE1
IGE:			CALL    ICP
IGE1:			RET     C
        		JR      TRUE_FP
;
FLE:			CALL    FCP
        		JR      ILE1
ILE:			CALL    ICP
ILE1:			JR      Z,TRUE_FP
        		RET     NC
        		JR      TRUE_FP
;
FNE:			CALL    FCP
        		JR      INE1
INE:			CALL    ICP
INE1:			RET     Z
        		JR      TRUE_FP
;
FEQ:			CALL    FCP
        		JR      IEQ1
IEQ:			CALL    ICP
IEQ1:			RET     NZ
TRUE_FP:			LD      HL,-1
        		EXX
        		LD      HL,-1
        		EXX
        		XOR     A
        		LD      C,A
        		RET
;
;FUNCTIONS:
;
;Result returned in HLH'L'C (floating point)
;Result returned in HLH'L' (C=0) (integer)
;All registers except IY destroyed.
;
;ABS - Absolute value
;Result is numeric, variable type.
;
ABSV_FP:			BIT     7,H
        		RET     Z               ;POSITIVE/ZERO
        		DEC     C
        		INC     C
        		JP      Z,NEGATE        ;INTEGER
        		RES     7,H
        		RET
;
;NOT - Complement integer.
;Result is integer numeric.
;
NOTK_FP:			CALL    SFIX_FP
        		LD      A,H
        		CPL
        		LD      H,A
        		LD      A,L
        		CPL
        		LD      L,A
        		EXX
        		LD      A,H
        		CPL
        		LD      H,A
        		LD      A,L
        		CPL
        		LD      L,A
        		EXX
        		XOR     A               ;NUMERIC MARKER
        		RET
;
;PI - Return PI (3.141592654)
;Result is floating-point numeric.
;
PI_FP:			LD      HL,490FH
        		EXX
        		LD      HL,0DAA2H
        		EXX
        		LD      C,81H
        		XOR     A               ;NUMERIC MARKER
        		RET
;
;DEG - Convert radians to degrees
;Result is floating-point numeric.
;
DEG_FP:			CALL    FPI180
        		CALL    FMUL
        		XOR     A
        		RET
;
;RAD - Convert degrees to radians
;Result is floating-point numeric.
;
RAD_FP:			CALL    FPI180
        		CALL    FDIV
        		XOR     A
        		RET
;
;180/PI
;
FPI180:			CALL    SFLOAT_FP
        		LD      DE,652EH
        		EXX
        		LD      DE,0E0D3H
        		EXX
        		LD      B,85H
        		RET
;
;SGN - Return -1, 0 or +1
;Result is integer numeric.
;
SGN_FP:			CALL    TEST_FP
        		OR      C
        		RET     Z               ;ZERO
        		BIT     7,H
        		JP      NZ,TRUE_FP         ;-1
        		CALL    ZERO_FP
        		JP      ADD1_FP            ;1
;
;VAL - Return numeric value of string.
;Input: ASCII string at IX
;Result is variable type numeric.
;
VAL_FP:			CALL    SIGNQ
        		PUSH    AF
        		CALL    CON_FP
        		POP     AF
        		CP      '-'
        		LD      A,0             ;NUMERIC MARKER
        		RET     NZ
        		DEC     C
        		INC     C
        		JP      Z,NEGATE        ;ZERO/INTEGER
        		LD      A,H
        		XOR     80H             ;CHANGE SIGN (FP)
        		LD      H,A
        		XOR     A
        		RET
;
;INT - Floor function
;Result is integer numeric.
;
INT_FP_:			DEC     C
        		INC     C
        		RET     Z               ;ZERO/INTEGER
        		LD      A,159
        		LD      B,H             ;B7=SIGN BIT
        		CALL    FIX
        		EX      AF,AF'
        		AND     B
        		CALL    M,ADD1_FP          ;NEGATIVE NON-INTEGER
        		LD      A,B
        		OR      A
        		CALL    M,NEGATE
        		XOR     A
        		LD      C,A
        		RET
;
;SQR - square root
;Result is floating-point numeric.
;
SQR_FP:			CALL    SFLOAT_FP
SQR0:			BIT     7,H
        		LD      A,NGROOT
        		JP      NZ,ERROR_FP_        ;"-ve root"
        		DEC     C
        		INC     C
        		RET     Z               ;ZERO
        		SET     7,H             ;IMPLIED 1
        		BIT     0,C
        		CALL    Z,DIV2          ;MAKE EXPONENT ODD
        		LD      A,C
        		SUB     80H
        		SRA     A               ;HALVE EXPONENT
        		ADD     A,80H
        		LD      C,A
        		PUSH    BC              ;SAVE EXPONENT
        		EX      DE,HL
        		LD      HL,0
        		LD      B,H
        		LD      C,L
        		EXX
        		EX      DE,HL
        		LD      HL,0
        		LD      B,H
        		LD      C,L
        		LD      A,-31
        		CALL    SQRA            ;ROOT
        		EXX
        		BIT     7,B
        		EXX
        		CALL    Z,SQRA          ;NORMALISE & INC A
        		CALL    SQRB
        		OR      A               ;CLEAR CARRY
        		CALL    DIVB
        		RR      E               ;LSB TO CARRY
        		LD      H,B
        		LD      L,C
        		EXX
        		LD      H,B
        		LD      L,C
        		CALL    C,ADD1_FP          ;ROUND UP
        		POP     BC              ;RESTORE EXPONENT
        		CALL    C,INCC
        		RRA
        		SBC     A,A
        		ADD     A,C
        		LD      C,A
        		RES     7,H             ;POSITIVE
        		XOR     A
        		RET
;
;TAN - Tangent function
;Result is floating-point numeric.
;
TAN_FP:			CALL    SFLOAT_FP
        		CALL    PUSH5
        		CALL    COS0
        		CALL    POP5
        		CALL    PUSH5
        		CALL    SWAP_FP
        		CALL    SIN0
        		CALL    POP5
        		CALL    FDIV
        		XOR     A               ;NUMERIC MARKER
        		RET
;
;COS - Cosine function
;Result is floating-point numeric.
;
COS_FP:			CALL    SFLOAT_FP
COS0:			CALL    SCALE
        		INC     E
        		INC     E
        		LD      A,E
        		JR      SIN1
;
;SIN - Sine function
;Result is floating-point numeric.
;
SIN_FP:			CALL    SFLOAT_FP
SIN0:			PUSH    HL              ;H7=SIGN
        		CALL    SCALE
        		POP     AF
        		RLCA
        		RLCA
        		RLCA
        		AND     4
        		XOR     E
SIN1:			PUSH    AF              ;OCTANT
        		RES     7,H
        		RRA
        		CALL    PIBY4
        		CALL    C,RSUB          ;X=(PI/4)-X
        		POP     AF
        		PUSH    AF
        		AND     3
        		JP      PO,SIN2         ;USE COSINE APPROX.
        		CALL    PUSH5           ;SAVE X
        		CALL    SQUARE          ;PUSH X*X
        		CALL    POLY
        		DW	0A8B7H          ;a(8)
        		DW	3611H
        		DB	6DH
        		DW	0DE26H          ;a(6)
        		DW	0D005H
        		DB	73H
        		DW	80C0H           ;a(4)
        		DW	888H
        		DB	79H
        		DW	0AA9DH          ;a(2)
        		DW	0AAAAH
        		DB	7DH
        		DW	0               ;a(0)
        		DW	0
        		DB	80H
        		CALL    POP5
        		CALL    POP5
        		CALL    FMUL
        		JP      SIN3
;
SIN2:			CALL    SQUARE          ;PUSH X*X
        		CALL    POLY
        		DW	0D571H          ;b(8)
        		DW	4C78H
        		DB	70H
        		DW	94AFH           ;b(6)
        		DW	0B603H
        		DB	76H
        		DW	9CC8H           ;b(4)
        		DW	2AAAH
        		DB	7BH
        		DW	0FFDDH          ;b(2)
        		DW	0FFFFH
        		DB	7EH
        		DW	0               ;b(0)
        		DW	0
        		DB	80H
        		CALL    POP5
SIN3:			POP     AF
        		AND     4
        		RET     Z
        		DEC     C
        		INC     C
        		RET     Z               ;ZERO
        		SET     7,H             ;MAKE NEGATIVE
        		RET
;
;Floating-point one:
;
FONE_FP:			LD      HL,0
        		EXX
        		LD      HL,0
        		EXX
        		LD      C,80H
        		RET
;
DONE:			LD      DE,0
        		EXX
        		LD      DE,0
        		EXX
        		LD      B,80H
        		RET
;
PIBY4:			LD      DE,490FH
        		EXX
        		LD      DE,0DAA2H
        		EXX
        		LD      B,7FH
        		RET
;
;EXP - Exponential function
;Result is floating-point numeric.
;
EXP_FP:			CALL    SFLOAT_FP
EXP0:			CALL    LN2             ;LN(2)
        		EXX
	        	DEC     E
		        LD      BC,0D1CFH       ;0.6931471805599453
        		EXX
        		PUSH    HL              ;H7=SIGN
        		CALL    MOD48           ;"MODULUS"
        		POP     AF
        		BIT     7,E
        		JR      Z,EXP1
        		RLA
        		JP      C,ZERO_FP
        		LD      A,EXPRNG
        		JP      ERROR_FP_           ;"Exp range"
;
EXP1:			AND     80H
        		OR      E
        		PUSH    AF              ;INTEGER PART
        		RES     7,H
        		CALL    PUSH5           ;PUSH X*LN(2)
        		CALL    POLY
        		DW	4072H           ;a(7)
        		DW	942EH
        		DB	73H
        		DW	6F65H           ;a(6)
        		DW	2E4FH
        		DB	76H
        		DW	6D37H           ;a(5)
        		DW	8802H
        		DB	79H
        		DW	0E512H          ;a(4)
        		DW	2AA0H
        		DB	7BH
        		DW	4F14H           ;a(3)
        		DW	0AAAAH
        		DB	7DH
        		DW	0FD56H          ;a(2)
        		DW	7FFFH
        		DB	7EH
        		DW	0FFFEH          ;a(1)
        		DW	0FFFFH
        		DB	7FH
        		DW	0               ;a(0)
        		DW	0
        		DB	80H
        		CALL    POP5
        		POP     AF
        		PUSH    AF
        		CALL    P,RECIP         ;X=1/X
        		POP     AF
        		JP      P,EXP4
        		AND     7FH
        		NEG
EXP4:			ADD     A,80H
        		ADD     A,C
        		JR      C,EXP2
        		JP      P,ZERO_FP          ;UNDERFLOW
        		JR      EXP3
EXP2:			JP      M,OFLOW         ;OVERFLOW
EXP3:			ADD     A,80H
        		JP      Z,ZERO_FP
        		LD      C,A
        		XOR     A               ;NUMERIC MARKER
        		RET
;
RECIP:			CALL    DONE
RDIV:			CALL    SWAP_FP
        		JP      FDIV            ;RECIPROCAL
;
LN2:			LD      DE,3172H        ;LN(2)
        		EXX
        		LD      DE,17F8H
        		EXX
        		LD      B,7FH
        		RET
;
;LN - Natural log.
;Result is floating-point numeric.
;
LN_FP:			CALL    SFLOAT_FP
LN0:			LD      A,LOGRNG
        		BIT     7,H
        		JP      NZ,ERROR_FP_        ;"Log range"
        		INC     C
        		DEC     C
        		JP      Z,ERROR_FP_
        		LD      DE,3504H        ;SQR(2)
        		EXX
        		LD      DE,0F333H       ;1.41421356237
        		EXX
        		CALL    ICP0            ;MANTISSA>SQR(2)?
        		LD      A,C             ;EXPONENT
        		LD      C,80H           ;1 <= X < 2
        		JR      C,LN4
        		DEC     C
        		INC     A
LN4:			PUSH    AF              ;SAVE EXPONENT
        		CALL    RATIO           ;X=(X-1)/(X+1)
        		CALL    PUSH5
		        CALL    SQUARE          ;PUSH X*X
        		CALL    POLY
        		DW	0CC48H          ;a(9)
        		DW	74FBH
        		DB	7DH
        		DW	0AEAFH          ;a(7)
        		DW	11FFH
        		DB	7EH
        		DW	0D98CH          ;a(5)
        		DW	4CCDH
        		DB	7EH
        		DW	0A9E3H          ;a(3)
        		DW	2AAAH
        		DB	7FH
        		DW	0               ;a(1)
        		DW	0
        		DB	81H
        		CALL    POP5
        		CALL    POP5
        		CALL    FMUL
        		POP     AF              ;EXPONENT
        		CALL    PUSH5
        		EX      AF,AF'
        		CALL    ZERO_FP
        		EX      AF,AF'
        		SUB     80H
        		JR      Z,LN3
        		JR      NC,LN1
        		CPL
        		INC     A
LN1:			LD      H,A
        		LD      C,87H
        		PUSH    AF
        		CALL    FLOAT_
        		RES     7,H
        		CALL    LN2
        		CALL    FMUL
        		POP     AF
        		JR      NC,LN3
        		JP      M,LN3
        		SET     7,H
LN3:			CALL    POP5
        		CALL    FADD
        		XOR     A
        		RET
;
;LOG - base-10 logarithm.
;Result is floating-point numeric.
;
LOG_FP:			CALL    LN_FP
        		LD      DE,5E5BH        ;LOG(e)
        		EXX
        		LD      DE,0D8A9H
        		EXX
        		LD      B,7EH
        		CALL    FMUL
        		XOR     A
        		RET
;
;ASN - Arc-sine
;Result is floating-point numeric.
;
ASN_FP:			CALL    SFLOAT_FP
        		CALL    PUSH5
        		CALL    COPY_
        		CALL    FMUL
        		CALL    DONE
        		CALL    RSUB
        		CALL    SQR0
        		CALL    POP5
        		INC     C
        		DEC     C
        		LD      A,2
        		PUSH    DE
        		JP      Z,ACS1
        		POP     DE
        		CALL    RDIV
        		JR      ATN0
;
;ATN - arc-tangent
;Result is floating-point numeric.
;
ATN_FP:			CALL    SFLOAT_FP
ATN0:			PUSH    HL              ;SAVE SIGN
        		RES     7,H
        		LD      DE,5413H        ;TAN(PI/8)=SQR(2)-1
        		EXX
        		LD      DE,0CCD0H
        		EXX
        		LD      B,7EH
        		CALL    FCP0            ;COMPARE
        		LD      B,0
        		JR      C,ATN2
        		LD      DE,1A82H        ;TAN(3*PI/8)=SQR(2)+1
        		EXX
        		LD      DE,799AH
        		EXX
        		LD      B,81H
        		CALL    FCP0            ;COMPARE
        		JR      C,ATN1
        		CALL    RECIP           ;X=1/X
        		LD      B,2
        		JP      ATN2
ATN1:			CALL    RATIO           ;X=(X-1)/(X+1)
        		LD      B,1
ATN2:			PUSH    BC              ;SAVE FLAG
        		CALL    PUSH5
        		CALL    SQUARE          ;PUSH X*X
        		CALL    POLY
        		DW	0F335H          ;a(13)
        		DW	37D8H
        		DB	7BH
        		DW	6B91H           ;a(11)
        		DW	0AAB9H
        		DB	7CH
        		DW	41DEH           ;a(9)
        		DW	6197H
        		DB	7CH
        		DW	9D7BH           ;a(7)
        		DW	9237H
        		DB	7DH
        		DW	2A5AH           ;a(5)
        		DW	4CCCH
        		DB	7DH
        		DW	0A95CH          ;a(3)
        		DW	0AAAAH
        		DB	7EH
        		DW	0               ;a(1)
        		DW	0
        		DB	80H
        		CALL    POP5
        		CALL    POP5
        		CALL    FMUL
        		POP     AF
ACS1:			CALL    PIBY4           ;PI/4
        		RRA
        		PUSH    AF
        		CALL    C,FADD
        		POP     AF
        		INC     B
        		RRA
        		CALL    C,RSUB
        		POP     AF
        		OR      A
        		RET     P
        		SET     7,H             ;MAKE NEGATIVE
        		XOR     A
        		RET
;
;ACS - Arc cosine=PI/2-ASN.
;Result is floating point numeric.
;
ACS_FP:			CALL    ASN_FP
        		LD      A,2
        		PUSH    AF
        		JR      ACS1
;
;Function STR - convert numeric value to ASCII string.
;   Inputs: HLH'L'C = integer or floating-point number
;           DE = address at which to store string
;           IX = address of @% format control
;  Outputs: String stored, with NUL terminator
;
;First normalise for decimal output:
;
STR_FP:			CALL    SFLOAT_FP
        		LD      B,0             ;DEFAULT PT. POSITION
        		BIT     7,H             ;NEGATIVE?
        		JR      Z,STR10
        		RES     7,H
        		LD      A,'-'
        		LD      (DE),A          ;STORE SIGN
        		INC     DE
STR10:			XOR     A               ;CLEAR A
        		CP      C
        		JR      Z,STR02          ;ZERO
        		PUSH    DE              ;SAVE TEXT POINTER
        		LD      A,B
STR11:			PUSH    AF              ;SAVE DECIMAL COUNTER
        		LD      A,C             ;BINARY EXPONENT
        		CP      161
        		JR      NC,STR14
        		CP      155
        		JR      NC,STR15
        		CPL
        		CP      225
        		JR      C,STR13
        		LD      A,-8
STR13:			ADD     A,28
        		CALL    POWR10
        		PUSH    AF
        		CALL    FMUL
        		POP     AF
        		LD      B,A
        		POP     AF
        		SUB     B
        		JR      STR11
STR14:			SUB     32
        		CALL    POWR10
        		PUSH    AF
        		CALL    FDIV
        		POP     AF
        		LD      B,A
        		POP     AF
        		ADD     A,B
        		JR      STR11
STR15:			LD      A,9
        		CALL    POWR10          ;10^9
        		CALL    FCP0
        		LD      A,C
        		POP     BC
        		LD      C,A
        		SET     7,H             ;IMPLIED 1
        		CALL    C,X10B          ;X10, DEC B
        		POP     DE              ;RESTORE TEXT POINTER
        		RES     7,C
        		LD      A,0
        		RLA                     ;PUT CARRY IN LSB
;
;At this point decimal normalisation has been done,
;now convert to decimal digits:
;      AHLH'L' = number in normalised integer form
;            B = decimal place adjustment
;            C = binary place adjustment (29-33)
;
STR02:			INC     C
        		EX      AF,AF'          ;SAVE A
        		LD      A,B
        		BIT     1,(IX+2)
        		JR      NZ,STR20
        		XOR     A
        		CP      (IX+1)
        		JR      Z,STR21
        		LD      A,-10
STR20:			ADD     A,(IX+1)        ;SIG. FIG. COUNT
        		OR      A               ;CLEAR CARRY
        		JP      M,STR21
        		XOR     A
STR21:			PUSH    AF
        		EX      AF,AF'          ;RESTORE A
STR22:			CALL    X2              ;RL AHLH'L'
        		ADC     A,A
        		CP      10
        		JR      C,STR23
        		SUB     10
        		EXX
        		INC     L               ;SET RESULT BIT
        		EXX
STR23:			DEC     C
        		JR      NZ,STR22        ;32 TIMES
        		LD      C,A             ;REMAINDER
        		LD      A,H
        		AND     3FH             ;CLEAR OUT JUNK
        		LD      H,A
        		POP     AF
        		JP      P,STR24
        		INC     A
        		JR      NZ,STR26
        		LD      A,4
        		CP      C               ;ROUND UP?
        		LD      A,0
        		JR      STR26
STR24:			PUSH    AF
        		LD      A,C
        		ADC     A,'0'           ;ADD CARRY
        		CP      '0'
        		JR      Z,STR25         ;SUPPRESS ZERO
        		CP      '9'+1
        		CCF
        		JR      NC,STR26
STR25:			EX      (SP),HL
        		BIT     6,L             ;ZERO FLAG
		        EX      (SP),HL
        		JR      NZ,STR27
        		LD      A,'0'
STR26:			INC     A               ;SET +VE
        		DEC     A
        		PUSH    AF              ;PUT ON STACK + CARRY
STR27:			INC     B
        		CALL    TEST_FP            ;IS HLH'L' ZERO?
        		LD      C,32
        		LD      A,0
        		JR      NZ,STR22
        		POP     AF
        		PUSH    AF
        		LD      A,0
        		JR      C,STR22
;
;At this point, the decimal character string is stored
; on the stack. Trailing zeroes are suppressed and may
; need to be replaced.
;B register holds decimal point position.
;Now format number and store as ASCII string:
;
STR3:			EX      DE,HL           ;STRING POINTER
        		LD      C,-1            ;FLAG "E"
        		LD      D,1
        		LD      E,(IX+1)        ;f2
        		BIT     0,(IX+2)
        		JR      NZ,STR34        ;E MODE
        		BIT     1,(IX+2)
        		JR      Z,STR31
        		LD      A,B             ;F MODE
        		OR      A
        		JR      Z,STR30
        		JP      M,STR30
        		LD      D,B
STR30:			LD      A,D
        		ADD     A,(IX+1)
        		LD      E,A
        		CP      11
        		JR      C,STR32
STR31:			LD      A,B             ;G MODE
        		LD      DE,101H
        		OR      A
        		JP      M,STR34
        		JR      Z,STR32
        		LD      A,(IX+1)
        		OR      A
        		JR      NZ,STR3A
        		LD      A,10
STR3A:			CP      B
        		JR      C,STR34
        		LD      D,B
        		LD      E,B
STR32:			LD      A,B
        		ADD     A,129
        		LD      C,A
STR34:			SET     7,D
        		DEC     E
STR35:			LD      A,D
        		CP      C
        		JR      NC,STR33
STR36:			POP     AF
        		JR      Z,STR37
        		JP      P,STR38
STR37:			PUSH    AF
        		INC     E
        		DEC     E
        		JP      M,STR4
STR33:			LD      A,'0'
STR38:			DEC     D
        		JP      PO,STR39
        		LD      (HL),'.'
        		INC     HL
STR39:			LD      (HL),A
        		INC     HL
        		DEC     E
        		JP      P,STR35
        		JR      STR36
;
STR4:			POP     AF
STR40:			INC     C
        		LD      C,L
        		JR      NZ,STR44
        		LD      (HL),'E'        ;EXPONENT
        		INC     HL
        		LD      A,B
        		DEC     A
        		JP      P,STR41
        		LD      (HL),'-'
        		INC     HL
        		NEG
STR41:			LD      (HL),'0'
        		JR      Z,STR47
        		CP      10
        		LD      B,A
        		LD      A,':'
        		JR      C,STR42
        		INC     HL
        		LD      (HL),'0'
STR42:			INC     (HL)
        		CP      (HL)
        		JR      NZ,STR43
        		LD      (HL),'0'
        		DEC     HL
        		INC     (HL)
        		INC     HL
STR43:			DJNZ    STR42
STR47:			INC     HL
STR44:			EX      DE,HL
      			RET
;
;Support subroutines:
;
DLOAD5:			LD      B,(IX+4)
        		EXX
        		LD      E,(IX+0)
        		LD      D,(IX+1)
        		EXX
        		LD      E,(IX+2)
        		LD      D,(IX+3)
        		RET
;
DLOAD5_SPL:		LD      B,(IX+6)
			EXX
			LD	DE, (IX+0)
			EXX
			LD	DE, (IX+3)
			RET
;
;CON_FP - Get unsigned numeric constant from ASCII string.
;   Inputs: ASCII string at (IX).
;  Outputs: Variable-type result in HLH'L'C
;           IX updated (points to delimiter)
;           A7 = 0 (numeric marker)
;
CON_FP:			CALL    ZERO_FP            ;INITIALISE TO ZERO
        		LD      C,0             ;TRUNCATION COUNTER
        		CALL    UINT          ;GET INTEGER PART
        		CP      '.'
        		LD      B,0             ;DECL. PLACE COUNTER
        		CALL    Z,NUMBIX        ;GET FRACTION PART
        		CP      'E'
        		LD      A,0             ;INITIALISE EXPONENT
        		CALL    Z,GETEXP        ;GET EXPONENT
        		BIT     7,H
        		JR      NZ,CON0         ;INTEGER OVERFLOW
        		OR      A
        		JR      NZ,CON0         ;EXPONENT NON-ZERO
        		CP      B
        		JR      NZ,CON0         ;DECIMAL POINT
        		CP      C
        		RET     Z               ;INTEGER
CON0:			SUB     B
        		ADD     A,C
        		LD      C,159
        		CALL    FLOAT_
        		RES     7,H             ;DITCH IMPLIED 1
        		OR      A
        		RET     Z               ;DONE
        		JP      M,CON2          ;NEGATIVE EXPONENT
        		CALL    POWR10
        		CALL    FMUL            ;SCALE
        		XOR     A
        		RET
CON2:			CP      -38
        		JR      C,CON3          ;CAN'T SCALE IN ONE GO
        		NEG
        		CALL    POWR10
        		CALL    FDIV            ;SCALE
        		XOR     A
        		RET
CON3:			PUSH    AF
        		LD      A,38
        		CALL    POWR10
        		CALL    FDIV
        		POP     AF
        		ADD     A,38
        		JR      CON2
;
;GETEXP - Get decimal exponent from string
;     Inputs: ASCII string at (IX)
;             (IX points at 'E')
;             A = initial value
;    Outputs: A = new exponent
;             IX updated.
;   Destroys: A,A',IX,F,F'
;
GETEXP:			PUSH    BC              ;SAVE REGISTERS
        		LD      B,A             ;INITIAL VALUE
        		LD      C,2             ;2 DIGITS MAX
        		INC     IX              ;BUMP PAST 'E'
        		CALL    SIGNQ
        		EX      AF,AF'          ;SAVE EXPONENT SIGN
GETEX1:			CALL    DIGITQ
        		JR      C,GETEX2
        		LD      A,B             ;B=B*10
        		ADD     A,A
        		ADD     A,A
        		ADD     A,B
        		ADD     A,A
        		LD      B,A
        		LD      A,(IX)          ;GET BACK DIGIT
        		INC     IX
        		AND     0FH             ;MASK UNWANTED BITS
        		ADD     A,B             ;ADD IN DIGIT
        		LD      B,A
        		DEC     C
        		JP      P,GETEX1
        		LD      B,100           ;FORCE OVERFLOW
        		JR      GETEX1
GETEX2:			EX      AF,AF'          ;RESTORE SIGN
        		CP      '-'
        		LD      A,B
        		POP     BC              ;RESTORE
        		RET     NZ
        		NEG                     ;NEGATE EXPONENT
        		RET
;
;UINT: Get unsigned integer from string.
;    Inputs: string at (IX)
;            C = truncated digit count
;                (initially zero)
;            B = total digit count
;            HLH'L' = initial value
;   Outputs: HLH'L' = number (binary integer)
;            A = delimiter.
;            B, C & IX updated
;  Destroys: A,B,C,D,E,H,L,B',C',D',E',H',L',IX,F
;
NUMBIX:			INC     IX
UINT:			CALL    DIGITQ
        		RET     C
        		INC     B               ;INCREMENT DIGIT COUNT
        		INC     IX
        		CALL    X10             ;*10 & COPY OLD VALUE
        		JR      C,NUMB1         ;OVERFLOW
        		DEC     C               ;SEE IF TRUNCATED
        		INC     C
        		JR      NZ,NUMB1        ;IMPORTANT!
        		AND     0FH
        		EXX
        		LD      B,0
        		LD      C,A
        		ADD.S   HL,BC           ;ADD IN DIGIT
        		EXX
        		JR      NC,UINT
        		INC.S   HL              ;CARRY
        		LD      A,H
        		OR      L
        		JR      NZ,UINT
NUMB1:			INC     C               ;TRUNCATION COUNTER
        		CALL    SWAP1           ;RESTORE PREVIOUS VALUE
        		JR      UINT
;
;FIX - Fix number to specified exponent value.
;    Inputs: HLH'L'C = +ve non-zero number (floated)
;            A = desired exponent (A>C)
;   Outputs: HLH'L'C = fixed number (unsigned)
;            fraction shifted into B'C'
;            A'F' positive if integer input
;  Destroys: C,H,L,A',B',C',H',L',F,F'
;
FIX:			EX      AF,AF'
        		XOR     A
        		EX      AF,AF'
        		SET     7,H             ;IMPLIED 1
FIX1:			CALL    DIV2
        		CP      C
        		RET     Z
        		JP      NC,FIX1
        		JP      OFLOW
;
;SFIX - Convert to integer if necessary.
;    Input: Variable-type number in HLH'L'C
;   Output: Integer in HLH'L', C=0
; Destroys: A,C,H,L,A',B',C',H',L',F,F'
;
;NEGATE - Negate HLH'L'
;    Destroys: H,L,H',L',F
;
FIX2:			CALL    SWAP_FP
        		CALL    SFIX_FP
        		CALL    SWAP_FP
SFIX_FP:			DEC     C
        		INC     C
        		RET     Z               ;INTEGER/ZERO
        		BIT     7,H             ;SIGN
        		PUSH    AF
        		LD      A,159
        		CALL    FIX
        		POP     AF
        		LD      C,0
        		RET     Z
NEGATE:			OR      A               ;CLEAR CARRY
        		EXX
NEG0:			PUSH    DE
        		EX      DE,HL
        		LD      HL,0
        		SBC.S   HL,DE
        		POP     DE
        		EXX
        		PUSH    DE
        		EX      DE,HL
        		LD      HL,0
        		SBC.S   HL,DE
        		POP     DE
        		RET
;
;NEG - Negate HLH'L'B'C'
;    Also complements A (used in FADD)
;    Destroys: A,H,L,B',C',H',L',F
;
NEG_:			EXX
        		CPL
        		PUSH    HL
        		OR      A               ;CLEAR CARRY
        		LD      HL,0
        		SBC.S   HL,BC
        		LD      B,H
        		LD      C,L
        		POP     HL
        		JR      NEG0
;
;SCALE - Trig scaling.
;MOD48 - 48-bit floating-point "modulus" (remainder).
;   Inputs: HLH'L'C unsigned floating-point dividend
;           DED'E'B'C'B unsigned 48-bit FP divisor
;  Outputs: HLH'L'C floating point remainder (H7=1)
;           E = quotient (bit 7 is sticky)
; Destroys: A,B,C,D,E,H,L,B',C',D',E',H',L',IX,F
;FLO48 - Float unsigned number (48 bits)
;    Input/output in HLH'L'B'C'C
;   Destroys: C,H,L,B',C',H',L',F
;
SCALE:			LD      A,150
        		CP      C
        		LD      A,ACLOST
        		JP      C,ERROR_FP_         ;"Accuracy lost"
        		CALL    PIBY4
        		EXX
        		LD      BC,2169H        ;3.141592653589793238
        		EXX
MOD48:			SET     7,D             ;IMPLIED 1
        		SET     7,H
        		LD      A,C
        		LD      C,0             ;INIT QUOTIENT
        		LD      IX,0
        		PUSH    IX              ;PUT ZERO ON STACK
        		CP      B
        		JR      C,MOD485        ;DIVIDEND<DIVISOR
MOD481:			EXX                     ;CARRY=0 HERE
        		EX      (SP),HL
        		SBC.S   HL,BC
        		EX      (SP),HL
        		SBC.S   HL,DE
        		EXX
        		SBC.S   HL,DE
        		JR      NC,MOD482       ;DIVIDEND>=DIVISOR
        		EXX
        		EX      (SP),HL
        		ADD.S   HL,BC
        		EX      (SP),HL
        		ADC.S   HL,DE
        		EXX
        		ADC.S   HL,DE
MOD482:			CCF
        		RL      C               ;QUOTIENT
        		JR      NC,MOD483
        		SET     7,C             ;STICKY BIT
MOD483:			DEC     A
        		CP      B
        		JR      C,MOD484        ;DIVIDEND<DIVISOR
        		EX      (SP),HL
        		ADD.S   HL,HL           ;DIVIDEND * 2
        		EX      (SP),HL
        		EXX
        		ADC.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		JR      NC,MOD481       ;AGAIN
        		OR      A
        		EXX
        		EX      (SP),HL
        		SBC.S   HL,BC           ;OVERFLOW, SO SUBTRACT
        		EX      (SP),HL
        		SBC.S   HL,DE
        		EXX
        		SBC.S   HL,DE
        		OR      A
        		JR      MOD482
;
MOD484:			INC     A
MOD485:			LD      E,C             ;QUOTIENT
        		LD      C,A             ;REMAINDER EXPONENT
        		EXX
        		POP     BC
        		EXX
FLO48:			BIT     7,H
        		RET     NZ
        		EXX
        		SLA     C
        		RL      B
        		ADC.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		DEC     C
        		JP      NZ,FLO48
        		RET
;
;Float unsigned number
;    Input/output in HLH'L'C
;   Destroys: C,H,L,H',L',F
;
FLOAT_:			BIT     7,H
        		RET     NZ
        		EXX                     ;SAME AS "X2"
        		ADD.S   HL,HL           ;TIME-CRITICAL
        		EXX                     ;REGION
        		ADC.S   HL,HL           ;(BENCHMARKS)
        		DEC     C
        		JP      NZ,FLOAT_
        		RET
;
;SFLOAT - Convert to floating-point if necessary.
;    Input: Variable-type number in HLH'L'C
;    Output: Floating-point in HLH'L'C
;    Destroys: A,C,H,L,H',L',F
;
FLOATA:			EX      AF,AF'
        		; ADD     A,(RTABLE-DTABLE)/3
        		ADD     A,RTABLE-DTABLE/3 ; ez80asm doesn't do nested expressions        		
        		EX      AF,AF'
FLOAT2:			CALL    SWAP_FP
        		CALL    SFLOAT_FP
        		CALL    SWAP_FP
SFLOAT_FP:			DEC     C
        		INC     C
        		RET     NZ              ;ALREADY FLOATING-POINT
        		CALL    TEST_FP
        		RET     Z               ;ZERO
        		LD      A,H
        		OR      A
        		CALL    M,NEGATE
        		LD      C,159
        		CALL    FLOAT_
        		OR      A
        		RET     M               ;NEGATIVE
        		RES     7,H
        		RET
;
;ROUND UP
;Return with carry set if 32-bit overflow
;   Destroys: H,L,B',C',H',L',F
;
ADD1_FP:			EXX
        		LD      BC,1
        		ADD.S   HL,BC
        		EXX
        		RET     NC
        		PUSH    BC
        		LD      BC,1
        		ADD.S   HL,BC
        		POP     BC
        		RET
;
;ODD - Add one if even, leave alone if odd.
; (Used to perform unbiassed rounding, i.e.
;  number is rounded up half the time)
;    Destroys: L',F (carry cleared)
;
ODD:			OR      A               ;CLEAR CARRY
        		EXX
        		SET     0,L             ;MAKE ODD
        		EXX
        		RET
;
;SWAP_FP - Swap arguments.
;    Exchanges DE,HL D'E',H'L' and B,C
;    Destroys: A,B,C,D,E,H,L,D',E',H',L'
;SWAP1 - Swap DEHL with D'E'H'L'
;    Destroys: D,E,H,L,D',E',H',L'
;
SWAP_FP:			LD      A,C
        		LD      C,B
        		LD      B,A
SWAP1:			EX      DE,HL
        		EXX
        		EX      DE,HL
        		EXX
        		RET
;
; DIV2 - destroys C,H,L,A',B',C',H',L',F,F'
; INCC - destroys C,F
; OFLOW
;
DIV2:			CALL    D2
        		EXX
        		RR      B
        		RR      C
        		EX      AF,AF'
        		OR      B
        		EX      AF,AF'
        		EXX
INCC:			INC     C
        		RET     NZ
OFLOW:			LD      A,TOOBIG_FP
        		JP      ERROR_FP_           ;"Too big"
;
; FTEST - Test for zero & sign
;     Output: A=0 if zero, A=&40 if +ve, A=&C0 if -ve
;
FTEST_FP:			CALL    TEST_FP
        		RET     Z
        		LD      A,H
        		AND     10000000B
        		OR      01000000B
        		RET
;
; TEST_FP - Test HLH'L' for zero.
;     Output: Z-flag set & A=0 if HLH'L'=0
;     Destroys: A,F
;
TEST_FP:			LD      A,H
        		OR      L
        		EXX
        		OR      H
        		OR      L
        		EXX
        		RET
;
; FCOMP - Compare two numbers
;     Output: A=0 if equal, A=&40 if L>R, A=&C0 if L<R
;
FCOMP_FP:			LD      A,B
        		OR      C               ;Both integer?
        		JR      NZ,FCOMP1
        		CALL    ICP
FCOMP0:			LD      A,0
        		RET     Z               ;Equal
        		LD      A,80H
        		RRA
        		RET
;
FCOMP1:			CALL    FLOAT2          ;Float both
        		CALL    FCP
        		JR      FCOMP0
;
; Integer and floating point compare.
; Sets carry & zero flags according to HLH'L'C-DED'E'B
; Result pre-set to FALSE
; ICP1, FCP1 destroy A,F
;
; ZERO - Return zero.
;  Destroys: A,C,H,L,H',L'
;
ICP:			CALL    ICP1
ZERO_FP:			LD      A,0
        		EXX
        		LD      H,A
	       		LD      L,A
        		EXX
      			LD      H,A
     			LD      L,A
	    		LD      C,A
        		RET
;
FCP:			CALL    FCP1
        		JR      ZERO_FP            ;PRESET FALSE
;
FCP0:			LD      A,C
        		CP      B               ;COMPARE EXPONENTS
        		RET     NZ
ICP0:			
			SBC.S   HL,DE           ;COMP MANTISSA MSB
        		ADD.S   HL,DE
        		RET     NZ
        		EXX
        		SBC.S   HL,DE           ;COMP MANTISSA LSB
        		ADD.S   HL,DE
        		EXX
        		RET
;
FCP1:			LD      A,H
        		XOR     D
        		LD      A,H
        		RLA
        		RET     M
        		JR      NC,FCP0
        		CALL    FCP0
        		RET     Z               ;** V0.1 BUG FIX
        		CCF
        		RET
;
ICP1:			LD      A,H
        		XOR     D
        		JP      P,ICP0
        		LD      A,H
        		RLA
        		RET
;
; ADD - Integer add.
; Carry, sign & zero flags valid on exit
;     Destroys: H,L,H',L',F
;
X10B:			DEC     B
        		INC     C
X5:			CALL    COPY0
        		CALL    D2C
        		CALL    D2C
        		EX      AF,AF'          ;SAVE CARRY
ADD_:			EXX
        		ADD.S   HL,DE
        		EXX
        		ADC.S   HL,DE
        		RET
;
; SUB - Integer subtract.
; Carry, sign & zero flags valid on exit
;     Destroys: H,L,H',L',F
;
SUB_:			EXX
        		OR      A
        		SBC.S   HL,DE
        		EXX
        		SBC.S   HL,DE
        		RET
;
; X10 - unsigned integer * 10
;    Inputs: HLH'L' initial value
;   Outputs: DED'E' = initial HLH'L'
;            Carry bit set if overflow
;            If carry not set HLH'L'=result
;  Destroys: D,E,H,L,D',E',H',L',F
; X2 - Multiply HLH'L' by 2 as 32-bit integer.
;     Carry set if MSB=1 before shift.
;     Sign set if MSB=1 after shift.
;     Destroys: H,L,H',L',F
;
X10:			CALL    COPY0           ;DED'E'=HLH'L'
        		CALL    X2
        		RET     C               ;TOO BIG
        		CALL    X2
        		RET     C
        		CALL    ADD_
        		RET     C
X2:			EXX
        		ADD.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		RET
;
; D2 - Divide HLH'L' by 2 as 32-bit integer.
;     Carry set if LSB=1 before shift.
;     Destroys: H,L,H',L',F
;
D2C:			INC     C
D2:			SRL     H
        		RR      L
        		EXX
        		RR      H
        		RR      L
        		EXX
        		RET
;
; COPY - COPY HLH'L'C INTO DED'E'B
;   Destroys: B,C,D,E,H,L,D',E',H',L'
;
COPY_:			LD      B,C
COPY0:			LD      D,H
        		LD      E,L
        		EXX
        		LD      D,H
        		LD      E,L
        		EXX
        		RET
;
; SQUARE - PUSH X*X
; PUSH5 - PUSH HLH'L'C ONTO STACK.
;   Destroys: SP,IX
;
SQUARE:			CALL    COPY_
        		CALL    FMUL
PUSH5:			POP     IX              ;RETURN ADDRESS
        		PUSH    BC
        		PUSH    HL
        		EXX
        		PUSH    HL
        		EXX
        		JP      (IX)            ;"RETURN"
;
; POP5 - POP DED'E'B OFF STACK.
;   Destroys: A,B,D,E,D',E',SP,IX
;
POP5:			POP     IX              ;RETURN ADDRESS
        		EXX
        		POP     DE
        		EXX
        		POP     DE
        		LD      A,C
        		POP     BC
        		LD      B,C
        		LD      C,A
        		JP      (IX)            ;"RETURN"
;
; RATIO - Calculate (X-1)/(X+1)
;     Inputs: X in HLH'L'C
;    Outputs: (X-1)/(X+1) in HLH'L'C
;   Destroys: Everything except IY,SP,I
;
RATIO:			CALL    PUSH5           ;SAVE X
        		CALL    DONE
        		CALL    FADD
        		CALL    POP5            ;RESTORE X
        		CALL    PUSH5           ;SAVE X+1
        		CALL    SWAP_FP
        		CALL    DONE
        		CALL    FSUB
        		CALL    POP5            ;RESTORE X+1
        		JP      FDIV
;
; POLY - Evaluate a polynomial.
;     Inputs: X in HLH'L'C and also stored at (SP+2)
;             Polynomial coefficients follow call.
;    Outputs: Result in HLH'L'C
;   Destroys: Everything except IY,SP,I
; Routine terminates on finding a coefficient >=1.
; Note: The last coefficient is EXECUTED on return
;       so must contain only innocuous bytes!
;
POLY:			LD      IX, 3				; Advance the SP to the return address
        		ADD     IX, SP				
        		EX      (SP), IX			; IX: Points to the inline list of coefficients
;		
        		CALL    DLOAD5          		; Load the first coefficient from (IX)
POLY1:			CALL    FMUL
        		LD      DE, 5				; Skip to the next coefficient
        		ADD     IX, DE		
        		CALL    DLOAD5          		; Load the second coefficient from (IX)
        		EX      (SP), IX			; Restore the SP just in case we need to return
        		INC     B		
        		DEC     B               		; Test B for end byte (80h)
        		JP      M,FADD				; Yes, so add and return
        		CALL    FADD				; No, so add
        		CALL    DLOAD5_SPL			; Load X from SP
        		EX      (SP), IX			; IX: Points to the inline list of coefficients
        		JR      POLY1				; And loop
;
; POWR10 - Calculate power of ten.
;     Inputs: A=power of 10 required (A<128)
;             A=binary exponent to be exceeded (A>=128)
;    Outputs: DED'E'B = result
;             A = actual power of ten returned
;   Destroys: A,B,D,E,A',D',E',F,F'
;
POWR10:			INC     A
        		EX      AF,AF'
        		PUSH    HL
        		EXX
        		PUSH    HL
        		EXX
        		CALL    DONE
        		CALL    SWAP_FP
        		XOR     A
POWR11:			EX      AF,AF'
        		DEC     A
        		JR      Z,POWR14        ;EXIT TYPE 1
        		JP      P,POWR13
        		CP      C
        		JR      C,POWR14        ;EXIT TYPE 2
        		INC     A
POWR13:			EX      AF,AF'
        		INC     A
        		SET     7,H
        		CALL    X5
        		JR      NC,POWR12
        		EX      AF,AF'
        		CALL    D2C
        		EX      AF,AF'
POWR12:			EX      AF,AF'
        		CALL    C,ADD1_FP          ;ROUND UP
        		INC     C
        		JP      M,POWR11
        		JP      OFLOW
POWR14:			CALL    SWAP_FP
        		RES     7,D
        		EXX
        		POP     HL
        		EXX
        		POP     HL
        		EX      AF,AF'
        		RET
;
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
;
; SQRA, SQRB - SQUARE ROOT PRIMITIVES
;     Function: B'C'BC = SQR (D'E'DE)
;     Inputs: A = loop counter (normally -31)
;             B'C'BCH'L'HL initialised to 0
;   Destroys: A,B,C,D,E,H,L,B',C',D',E',H',L',F
;
SQR1:			
			SBC.S   HL,BC
        		EXX
        		SBC.S   HL,BC
        		EXX
        		INC     C
        		JR      NC,SQR2
        		DEC     C
        		ADD.S   HL,BC
        		EXX
        		ADC.S   HL,BC
        		EXX
        		DEC     C
SQR2:			INC     A
        		RET     P
SQRA:			SLA     C
        		RL      B
        		EXX
        		RL      C
        		RL      B
        		EXX
        		INC     C
        		SLA     E
        		RL      D
        		EXX
        		RL      E
        		RL      D
        		EXX
        		ADC.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		EXX
        		SLA     E
        		RL      D
        		EXX
        		RL      E
        		RL      D
        		EXX
        		ADC.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		EXX
        		JP      NC,SQR1
SQR3:			OR      A
        		SBC.S   HL,BC
        		EXX
        		SBC.S   HL,BC
        		EXX
        		INC     C
        		JP      SQR2
;
SQRB:			
			ADD.S   HL,HL
        		EXX
        		ADC.S   HL,HL
        		EXX
        		JR      C,SQR3
        		INC     A
        		INC     C
        		SBC.S   HL,BC
        		EXX
        		SBC.S   HL,BC
        		EXX
        		RET     NC
        		ADD.S   HL,BC
        		EXX
        		ADC.S   HL,BC
        		EXX
        		DEC     C
        		RET
;
DIGITQ:			LD      A,(IX)
        		CP      '9'+1
        		CCF
        		RET     C
        		CP      '0'
        		RET
;
SIGNQ:			LD      A,(IX)
        		INC     IX
        		CP      ' '
        		JR      Z,SIGNQ
        		CP      '+'
        		RET     Z
        		CP      '-'
        		RET     Z
        		DEC     IX
        		RET

; ==============================================================================
; from functions.inc
; ------------------------------------------------------------------------------

; test the sign of HL
; inputs: HL obviously
; outputs: sign flag set if HL is negative, zero flag set if HL is zero
; destroys: flags    
    MACRO sign_hlu
        add hl,de
        or a
        sbc hl,de
    ENDMACRO

    MACRO PUSH_ALL
        ex af,af'
        exx
        push af
        push hl
        push bc
        push de

        ex af,af'
        exx
        push af
        push hl
        push bc
        push de
        push ix
        push iy
    ENDMACRO

    MACRO POP_ALL
        pop iy
        pop ix
        pop de
        pop bc
        pop hl
        pop af
        ex af,af'
        exx

        pop de
        pop bc
        pop hl
        pop af
        ex af,af'
        exx
    ENDMACRO

; put the value in HLU into the accumulator
; destroys: af
    MACRO HLU_TO_A
        push hl ; 4 cycles
        inc sp ; 1 cycle
        pop af  ; 4 cycles
        dec sp ; 1 cycle
               ; 10 cycles total
    ENDMACRO

A_TO_HLU:
    ; call is 7 cycles
    ld (@scratch),hl ; 7 cycles
    ld (@scratch+2),a ; 5 cycles
    ld hl,(@scratch) ; 7 cycles
    ret ; 6 cycles
        ; 25 cycles total
@scratch: dl 0

; https://github.com/envenomator/Agon/blob/master/ez80asm%20examples%20(annotated)/functions.s
; Print a zero-terminated string
; HL: Pointer to string
printString:
	PUSH	BC
	LD		BC,0
	LD 	 	A,0
	RST.LIL 18h
	POP		BC
	RET

; Print Newline sequence to VDP
printNewLine:
    push af ; for some reason rst.lil 10h sets carry flag
	LD	A, '\r'
	RST.LIL 10h
	LD	A, '\n'
	RST.LIL 10h
    pop af
	RET

; ==============================================================================
; from mathfpp.inc
; ------------------------------------------------------------------------------

; integer operations		
iand:	EQU 58	; AND (INTEGER)
ibdiv:	EQU 59	; DIV
ieor:	EQU 60	; EOR
imod:	EQU 61	; MOD
ior:	EQU 62	; OR
ile:	EQU 63	; <=
ine:	EQU 64	; <>
ige:	EQU 65	; >=
ilt:	EQU 66	; <
ieq:	EQU 67	; =
imul:	EQU 68	; *
iadd:	EQU 69	; +
igt:	EQU 70	; >
isub:	EQU 71	; -
ipow:	EQU 72	; ^
idiv:	EQU 73	; /
;		
; floating point functions		
absv:	EQU 16	; ABS
acs:	EQU 17	; ACS
asn:	EQU 18	; ASN
atn:	EQU 19	; ATN
cos:	EQU 20	; COS
deg:	EQU 21	; DEG
exp:	EQU 22	; EXP
int_:	EQU 23	; INT
ln:	    EQU 24	; LN
log:	EQU 25	; LOG
notk:	EQU 26	; NOT
rad:	EQU 27	; RAD
sgn:	EQU 28	; SGN
sin:	EQU 29	; SIN
sqr:	EQU 30	; SQR
tan:	EQU 31	; TAN
zero:	EQU 32	; ZERO
fone:	EQU 33	; FONE
true:	EQU 34	; TRUE
pi:	    EQU 35	; PI
val:	EQU 36	; VAL
str:	EQU 37	; STR$
sfix:	EQU 38	; FIX
sfloat:	EQU 39	; FLOAT
ftest:	EQU 40	; TEST
fcomp:	EQU 41	; COMPARE
;		
; floating point operations		
fand:	EQU  0	; AND (FLOATING-POINT)
fbdiv:	EQU  1	; DIV
feor:	EQU  2	; EOR
fmod:	EQU  3	; MOD
ffor:	EQU  4	; OR
fle:	EQU  5	; <=
fne:	EQU  6	; <>
fge:	EQU  7	; >=
flt:	EQU  8	; <
feq:	EQU  9	; =
fmul:	EQU 10	; *
fadd:	EQU 11	; +
fgt:	EQU 12	; >
fsub:	EQU 13	; -
fpow:	EQU 14	; ^
fdiv:	EQU 15	; /

    MACRO LOAD_FLOAT ARG
    ld ix,$+11
    call val_fp ; convert the string to a float
    jp (ix)
    asciz ARG
    ENDMACRO

; store HLH'L'C floating point number in a 40-bit buffer
; inputs: HLH'L'C = floating point number
;         ix = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_nor:
    ld (ix+0),c
    ld (ix+3),l
    ld (ix+4),h
    exx
    ld (ix+1),l
    ld (ix+2),h
    exx
    ret

; fetch HLH'L'C floating point number from a 40-bit buffer
; inputs: ix = buffer address
; outputs: HLH'L'C = floating point number
; destroys: HLH'L'C
fetch_float_nor:
    ld c,(ix+0)
    ld l,(ix+3)
    ld h,(ix+4)
    exx
    ld l,(ix+1)
    ld h,(ix+2)
    exx
    ret

; store DED'E'B floating point number in a 40-bit buffer
; inputs: DED'E'B = floating point number
;         ix = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_alt:
    ld (ix+0),b
    ld (ix+3),e
    ld (ix+4),d
    exx
    ld (ix+1),e
    ld (ix+2),d
    exx
    ret

; fetch DED'E'B floating point number from a 40-bit buffer
; inputs: ix = buffer address
; outputs: DED'E'B = floating point number
; destroys: DED'E'B
fetch_float_alt:
    ld b,(ix+0)
    ld e,(ix+3)
    ld d,(ix+4)
    exx
    ld e,(ix+1)
    ld d,(ix+2)
    exx
    ret

; store HLH'L'C floating point number in a 40-bit buffer
; inputs: HLH'L'C = floating point number
;         iy = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_iy_nor:
    ld (iy+0),c
    ld (iy+3),l
    ld (iy+4),h
    exx
    ld (iy+1),l
    ld (iy+2),h
    exx
    ret

; fetch HLH'L'C floating point number from a 40-bit buffer
; inputs: iy = buffer address
; outputs: HLH'L'C = floating point number
; destroys: HLH'L'C
fetch_float_iy_nor:
    ld c,(iy+0)
    ld l,(iy+3)
    ld h,(iy+4)
    exx
    ld l,(iy+1)
    ld h,(iy+2)
    exx
    ret

; store DED'E'B floating point number in a 40-bit buffer
; inputs: DED'E'B = floating point number
;         iy = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_iy_alt:
    ld (iy+0),b
    ld (iy+3),e
    ld (iy+4),d
    exx
    ld (iy+1),e
    ld (iy+2),d
    exx
    ret

; fetch DED'E'B floating point number from a 40-bit buffer
; inputs: iy = buffer address
; outputs: DED'E'B = floating point number
; destroys: DED'E'B
fetch_float_iy_alt:
    ld b,(iy+0)
    ld e,(iy+3)
    ld d,(iy+4)
    exx
    ld e,(iy+1)
    ld d,(iy+2)
    exx
    ret

;PI - Return PI * 2 (6.28318531)
;Result is floating-point numeric.
;
pi2_alt:		LD      DE,0x490F
        		EXX
        		LD      DE,0xDAA3
        		EXX
        		LD      B,0x82
        		XOR     A               ;NUMERIC MARKER
        		RET

; --- originally in eval.asm ---
;SWAP - Swap arguments
;Exchanges DE,HL D'E',H'L' and B,C
;Destroys: A,B,C,D,E,H,L,D',E',H',L'
;
SWAP:			LD      A,C
			LD      C,B
			LD      B,A
			EX      DE,HL
			EXX
			EX      DE,HL
			EXX
			RET

; same as VAL_FP in fpp.asm, but preserves any float stored in DED'E'B
val_fp:
    push iy ; preserve
    ld iy,@val
    call store_float_iy_alt
    ld a,val
    call FPP ; string converted to float in HLH'L'C
    ld iy,@val
    call fetch_float_iy_alt
    pop iy ; restore
    ret
@val: ds 5

; same as INT_FP_ in fpp.asm but preserves B, which keeps any float stored in DED'E'B intact
; af will also return differently from the original
;INT - Floor function
;Result is integer numeric.
;
int_fp_:		
    push bc ; preserve b
    ld a,int_
    call FPP
    pop af ; restore b to a
    ld b,a ; restore b
    RET

; convert floating point number to integer and store it in HLU
; inputs: HLH'L'C = floating point number
; outputs: HLU = integer part of the number
; destroys: all except DEU and U'D'E'B, index registers
int2hlu:
    call int_fp_
    ld a,l
    push af
    exx
    push hl
    exx
    pop hl
    pop af
    call A_TO_HLU
    ret

; convert polar coordinates to cartesian coordinates as deltas from the origin
; inputs: HLH'L'C = angle in radians
;         DED'E'B = radius
; outputs: HLH'L'C = dx
;          DED'E'B = dy
polar_to_cartesian_fpp:
; store input parameters in scratch
    ld iy,@angle
    call store_float_iy_nor
    ld iy,@radius
    call store_float_iy_alt
; compute dy = sin(angle) * radius
    ld a,sin
    call FPP ; HLH'L'C = sin(angle)
    ld iy,@radius
    call fetch_float_iy_alt ; DED'E'B = radius
    ld a,fmul
    call FPP ; HLH'L'C = sin(angle) * radius
    ld iy,@scratch
    call store_float_iy_nor ; @scratch = dy
; compute dx = cos(angle) * radius
    ld iy,@angle
    call fetch_float_iy_nor
    ld a,cos
    call FPP ; HLH'L'C = cos(angle)
    ld iy,@radius
    call fetch_float_iy_alt ; DED'E'B = radius
    ld a,fmul
    call FPP ; HLH'L'C = cos(angle) * radius
; restore dy from @scratch
    ld iy,@scratch
    call fetch_float_iy_alt
    ret
@angle: ds 5
@radius: ds 5
@scratch: ds 5

; print a floating point number in decimal format
; inputs: HL'H'L'C is the number to print
; outputs: number printed to screen
;          ACCS null-terminated string representation of the number
; destroys: everything except ix
print_float_dec:
print_float_dec_nor:
    push ix             ; preserve

; back up floats in normal and alternate registers
    ld ix,@float_nor   
    call store_float_nor
    ld ix,@float_alt
    call store_float_alt

; convert the number to a string
    ld de,ACCS          ; point to the string accumulator
    ld ix,@G9-1         ; get the format code for the number
    call STR_FP         ; convert the number to a string
    ex de,hl            ; point to end of the string
    ld (hl),0           ; null-terminate the string
    ld hl,ACCS          ; point to the string accumulator
    call printString

; restore floats in normal and alternate registers
    ld ix,@float_nor
    call fetch_float_nor
    ld ix,@float_alt
    call fetch_float_alt

; cleanup and go home
    pop ix              ; restore
    ret
@G9:			DW    9
@float_nor: ds 5
@float_alt: ds 5


; ==============================================================================
; from vdu.inc
; ------------------------------------------------------------------------------

; VDU 12: Clear text area (CLS)
vdu_cls:
    ld a,12
	rst.lil $10  
	ret

vdu_flip:       
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: db 23,0,0xC3
@end:

; VDU 29, x; y;: Set graphics origin
; This command sets the graphics origin. 
; The origin is the point on the screen where the coordinates (0,0) are located.
; inputs: bc=x0,de=y0
; outputs; nothing
; destroys: a might make it out alive
vdu_set_gfx_origin:
    ld (@x0),bc
    ld (@y0),de
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:   db 29 ; set graphics origin command
@x0: 	dw 0x0000 ; set by bc
@y0: 	dw 0x0000 ; set by de
@end:   db 0x00	  ; padding


; ==============================================================================
; from vdu_plot.inc
; ------------------------------------------------------------------------------

; https://agonconsole8.github.io/agon-docs/VDP---PLOT-Commands.html

; PLOT code 	(Decimal) 	Effect
; &00-&07 	0-7 	Solid line, includes both ends
plot_sl_both: equ 0x00

; &40-&47 	64-71 	Point plot
plot_pt: equ 0x40

; Plot code 	Effect
; 4 	Move absolute
mv_abs: equ 4

; 5 	Plot absolute in current foreground colour
dr_abs_fg: equ 5

; ==============================================================================
; from flower.asm
; ------------------------------------------------------------------------------
;
; ========================================
; MODIFIED MOSLET INITIALIZATION CODE
; ========================================
;
; Title:	Copy - Initialisation Code
; Author:	Dean Belfield, Lennart Benschop
; Created:	06/11/2022
; Last Updated:	26/12/2022
;
; Modinfo:
; 17/12/2022:	Added parameter processing
; 26/12/2022:   Adapted to Copy program, use LEA instead of 3x INC IX, Save/restore MB
; Changed:      08/04/2924 adapt to ez80asm
;
    ASSUME	ADL = 1			
    ; INCLUDE "mos_api.inc"
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
    ; include "basic/fpp.asm"
    ; include "functions.inc"
	; include "maths.inc"
    ; include "mathfpp.inc"
    ; include "vdu.inc"
    ; include "vdu_plot.inc"
    ; include "files.inc"

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
petals:             db   0x81, 0x1E, 0x85, 0xEB, 0x41           ; 3.03
vectors:            db   0x80, 0xD7, 0xA3, 0x70, 0x7D           ; 1.98
depth:              db   0x7F, 0x99, 0x99, 0x99, 0x19           ; 0.6
periods:            db   0x86, 0x00, 0x00, 0x00, 0x04           ; 66
shrink:             db   0x7F, 0xCC, 0xCC, 0xCC, 0x4C           ; 0.8
radius_scale: 	    db   0x88, 0x00, 0x00, 0x00, 0x00           ; 256
theta_init: 	    db   0x00, 0x00, 0x00, 0x00, 0x00           ; 0

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

; Calculate shrink per step (linear)
    ; step_shrink = -shrink * radius_scale / total_steps 
    ld iy,shrink
    call fetch_float_iy_nor
    ld iy,radius_scale
    call fetch_float_iy_alt
    ld a,fmul
    call FPP ; HLH'L'C = shrink * radius_scale

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

; Initialize radius_prime
    ld iy,radius_scale
    call fetch_float_iy_nor
    ld iy,radius_prime
    call store_float_iy_nor

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


; ==============================================================================
; from basic/ram.asm
; ------------------------------------------------------------------------------
;
; Title:	BBC Basic Interpreter - Z80 version
;		RAM Module for BBC Basic Interpreter
;		For use with Version 2.0 of BBC BASIC
;		Standard CP/M Distribution Version
; Author:	(C) Copyright  R.T.Russell 31-12-1983
; Modified By:	Dean Belfield
; Created:	12/05/2023
; Last Updated:	26/06/2023
;
; Modinfo:
; 06/06/2023:	Modified to run in ADL mode
; 26/06/2023:	Added temporary stores R0 and R1

			; .ASSUME	ADL = 1

			; DEFINE	LORAM, SPACE = ROM
			; SEGMENT LORAM

			; XDEF	ACCS
			; XDEF	BUFFER
			; XDEF	STAVAR
			; XDEF	DYNVAR
			; XDEF	FNPTR
			; XDEF	PROPTR
			; XDEF	PAGE_
			; XDEF	TOP
			; XDEF	LOMEM
			; XDEF 	FREE
			; XDEF	HIMEM
			; XDEF	LINENO
			; XDEF	TRACEN
			; XDEF	AUTONO
			; XDEF	ERRTRP
			; XDEF	ERRTXT
			; XDEF	DATPTR
			; XDEF	ERL
			; XDEF	ERRLIN
			; XDEF	RANDOM
			; XDEF	COUNT
			; XDEF	WIDTH
			; XDEF	ERR
			; XDEF	LISTON
			; XDEF	INCREM
			
			; XDEF	FLAGS
			; XDEF	OSWRCHPT
			; XDEF	OSWRCHCH
			; XDEF	OSWRCHFH
			; XDEF	KEYDOWN 
			; XDEF	KEYASCII
			; XDEF	KEYCOUNT

			; XDEF	R0
			; XDEF	R1
			
			; XDEF	RAM_START
			; XDEF	RAM_END
			; XDEF	USER

end_binary: ;  for assemble.py to know where to truncate the binary file
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
	