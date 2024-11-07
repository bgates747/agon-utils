; EQU Definitions
ACLOST:			EQU     23              ;Accuracy lost ; from fpp.asm
ANDK:			EQU     80H ; from eval.asm
BADOP:			EQU     1               ;Bad operation code ; from fpp.asm
CR:			EQU     0DH ; from equs.inc
DATA_:			EQU     DCH ; from exec.asm
DEF_:			EQU     DDH ; from exec.asm
DIVBY0:			EQU     18              ;Division by zero ; from fpp.asm
DIVK:			EQU     81H ; from eval.asm
ELSE_:			EQU     8BH ; from exec.asm
EORK:			EQU     82H ; from eval.asm
ESC:			EQU     1BH ; from equs.inc
EXPRNG:			EQU     24              ;Exp range ; from fpp.asm
FUNTOK:			EQU	8DH			; First token number ; from eval.asm
GPIOMODE_ALTF:		EQU		5;	; Alt Function ; from equs.inc
GPIOMODE_DIO:		EQU		2	; Open Drain IO ; from equs.inc
GPIOMODE_IN:		EQU		1	; Input ; from equs.inc
GPIOMODE_INTAH:		EQU		7	; Interrupt, Active High ; from equs.inc
GPIOMODE_INTAL:		EQU		6	; Interrupt, Active Low ; from equs.inc
GPIOMODE_INTD:		EQU		4	; Interrupt, Dual Edge ; from equs.inc
GPIOMODE_INTFE:		EQU		8	; Interrupt, Falling Edge ; from equs.inc
GPIOMODE_INTRE:		EQU		9	; Interrupt, Rising Edge ; from equs.inc
GPIOMODE_OUT:		EQU		0	; Output ; from equs.inc
GPIOMODE_SIO:		EQU		3	; Open Source IO ; from equs.inc
LF:			EQU     0AH ; from equs.inc
LINE_:			EQU     86H ; from exec.asm
LINO:			EQU     8DH ; from exec.asm
LOGRNG:			EQU     22              ;Log range ; from fpp.asm
MODK:			EQU     83H ; from eval.asm
NGROOT:			EQU     21              ;Negative root ; from fpp.asm
OC:			EQU     STAVAR+15*4     ; CODE ORIGIN (O%) ; from equs.inc
OFF_:			EQU     87H ; from exec.asm
ORK:			EQU     84H ; from eval.asm
PA_ALT1:		EQU		98h ; from equs.inc
PA_ALT2:		EQU		99h ; from equs.inc
PA_DDR:			EQU		97h ; from equs.inc
PA_DR:			EQU		96h ; from equs.inc
PB_ALT1:        	EQU		9Ch ; from equs.inc
PB_ALT2:        	EQU		9Dh ; from equs.inc
PB_DDR:        	 	EQU		9Bh ; from equs.inc
PB_DR:          	EQU		9Ah ; from equs.inc
PC:			EQU     STAVAR+16*4     ; PROGRAM COUNTER (P%) ; from equs.inc
PC_ALT1:        	EQU		A0h ; from equs.inc
PC_ALT2:        	EQU		A1h ; from equs.inc
PC_DDR:         	EQU		9Fh ; from equs.inc
PC_DR:          	EQU		9Eh ; from equs.inc
PD_ALT1:		EQU		A4h ; from equs.inc
PD_ALT2:		EQU		A5h ; from equs.inc
PD_DDR:			EQU		A3h ; from equs.inc
PD_DR:          	EQU		A2h ; from equs.inc
RAM_Top:		EQU		0B0000h	; Initial value of HIMEM ; from equs.inc
SIZEW:			EQU		3	; Size of a word (3 for ADL mode) ; from equs.inc
SPC:			EQU     89H ; from exec.asm
STEP:			EQU     88H ; from exec.asm
TAB:			EQU     8AH ; from exec.asm
TAND:			EQU     80H ; from exec.asm
TCALL:			EQU     D6H ; from exec.asm
TCMD:			EQU     FUNTBL_END-FUNTBL/3+FUNTOK ; reorder because ez80asm doesn't do order of operations ; from eval.asm
TCMD:			EQU     C6H ; from exec.asm
TERROR:			EQU     85H ; from exec.asm
TGOSUB:			EQU     E4H ; from exec.asm
TGOTO:			EQU     E5H ; from exec.asm
THEN:			EQU     8CH ; from exec.asm
TO:			EQU     B8H ; from exec.asm
TON:			EQU     EEH ; from exec.asm
TOOBIG:			EQU     20              ;Too big ; from fpp.asm
TOR:			EQU     84H ; from exec.asm
TPROC:			EQU     F2H ; from exec.asm
TSTOP:			EQU     FAH ; from exec.asm
VDU_BUFFER:		EQU	ACCS		; Storage for VDU commands ; from equs.inc
argv_ptrs_max:		EQU	16				; Maximum number of arguments allowed in argv ; from init.asm
fa_create_always:	EQU	08h ; from mos_api.inc
fa_create_new:		EQU	04h ; from mos_api.inc
fa_open_always:		EQU	10h ; from mos_api.inc
fa_open_append:		EQU	30h ; from mos_api.inc
fa_open_existing:	EQU	00h ; from mos_api.inc
fa_read:		EQU	01h ; from mos_api.inc
fa_write:		EQU	02h ; from mos_api.inc
ffs_chdir:		EQU	9Ch ; from mos_api.inc
ffs_chdrive:		EQU	9Dh ; from mos_api.inc
ffs_chmod:		EQU	99h ; from mos_api.inc
ffs_dclose:		EQU	92h ; from mos_api.inc
ffs_dfindfirst:		EQU	94h ; from mos_api.inc
ffs_dfindnext:		EQU	95h ; from mos_api.inc
ffs_dopen:		EQU	91h ; from mos_api.inc
ffs_dread:		EQU	93h ; from mos_api.inc
ffs_fclose:		EQU	81h ; from mos_api.inc
ffs_fdisk:		EQU	A1h ; from mos_api.inc
ffs_feof:		EQU	8Eh ; from mos_api.inc
ffs_ferror:		EQU	90h ; from mos_api.inc
ffs_fexpand:		EQU	88h ; from mos_api.inc
ffs_fforward:		EQU	87h ; from mos_api.inc
ffs_fgets:		EQU	89h ; from mos_api.inc
ffs_flseek:		EQU	84h ; from mos_api.inc
ffs_fopen:		EQU	80h ; from mos_api.inc
ffs_fprintf:		EQU	8Ch ; from mos_api.inc
ffs_fputc:		EQU	8Ah ; from mos_api.inc
ffs_fputs:		EQU	8Bh ; from mos_api.inc
ffs_fread:		EQU	82h ; from mos_api.inc
ffs_fsize:		EQU	8Fh ; from mos_api.inc
ffs_fsync:		EQU	86h ; from mos_api.inc
ffs_ftell:		EQU	8Dh ; from mos_api.inc
ffs_ftruncate:		EQU	85h ; from mos_api.inc
ffs_fwrite:		EQU	83h ; from mos_api.inc
ffs_getcwd:		EQU	9Eh ; from mos_api.inc
ffs_getfree:		EQU	A2h ; from mos_api.inc
ffs_getlabel:		EQU	A3h ; from mos_api.inc
ffs_mkdir:		EQU	9Bh ; from mos_api.inc
ffs_mkfs:		EQU	A0h ; from mos_api.inc
ffs_mount:		EQU	9Fh ; from mos_api.inc
ffs_rename:		EQU	98h ; from mos_api.inc
ffs_setcp:		EQU	A5h ; from mos_api.inc
ffs_setlabel:		EQU	A4h ; from mos_api.inc
ffs_stat:		EQU	96h ; from mos_api.inc
ffs_unlink:		EQU	97h ; from mos_api.inc
ffs_utime:		EQU	9Ah ; from mos_api.inc
mos_cd:			EQU	03h ; from mos_api.inc
mos_copy:		EQU	11h ; from mos_api.inc
mos_del:		EQU	05h ; from mos_api.inc
mos_dir:		EQU	04h ; from mos_api.inc
mos_editline:		EQU	09h ; from mos_api.inc
mos_fclose:		EQU	0Bh ; from mos_api.inc
mos_feof:		EQU	0Eh ; from mos_api.inc
mos_fgetc:		EQU	0Ch ; from mos_api.inc
mos_flseek:		EQU	1Ch ; from mos_api.inc
mos_fopen:		EQU	0Ah ; from mos_api.inc
mos_fputc:		EQU	0Dh ; from mos_api.inc
mos_fread:		EQU	1Ah ; from mos_api.inc
mos_fwrite:		EQU	1Bh ; from mos_api.inc
mos_getError:		EQU	0Fh ; from mos_api.inc
mos_getfil:		EQU	19h ; from mos_api.inc
mos_getkbmap:		EQU	1Eh ; from mos_api.inc
mos_getkey:		EQU	00h ; from mos_api.inc
mos_getrtc:		EQU	12h ; from mos_api.inc
mos_i2c_close:		EQU	20h ; from mos_api.inc
mos_i2c_open:		EQU	1Fh ; from mos_api.inc
mos_i2c_read:		EQU	22h ; from mos_api.inc
mos_i2c_write:		EQU	21h ; from mos_api.inc
mos_load:		EQU	01h ; from mos_api.inc
mos_mkdir:		EQU	07h ; from mos_api.inc
mos_oscli:		EQU	10h ; from mos_api.inc
mos_ren:		EQU	06h ; from mos_api.inc
mos_save:		EQU	02h ; from mos_api.inc
mos_setintvector:	EQU	14h ; from mos_api.inc
mos_setkbvector:	EQU	1Dh ; from mos_api.inc
mos_setrtc:		EQU	13h ; from mos_api.inc
mos_sysvars:		EQU	08h ; from mos_api.inc
mos_uclose:		EQU	16h ; from mos_api.inc
mos_ugetc:		EQU	17h ; from mos_api.inc
mos_uopen:		EQU	15h ; from mos_api.inc
mos_uputc:		EQU 	18h ; from mos_api.inc
sysvar_audioChannel:	EQU	0Dh	; 1: Audio channel ; from mos_api.inc
sysvar_audioSuccess:	EQU	0Eh	; 1: Audio channel note queued (0 = no, 1 = yes) ; from mos_api.inc
sysvar_cursorX:		EQU	07h	; 1: Cursor X position ; from mos_api.inc
sysvar_cursorY:		EQU	08h	; 1: Cursor Y position ; from mos_api.inc
sysvar_keyascii:	EQU	05h	; 1: ASCII keycode, or 0 if no key is pressed ; from mos_api.inc
sysvar_keydelay:	EQU	22h	; 2: Keyboard repeat delay ; from mos_api.inc
sysvar_keyled:		EQU	26h	; 1: Keyboard LED status ; from mos_api.inc
sysvar_keymods:		EQU	06h	; 1: Keycode modifiers ; from mos_api.inc
sysvar_keyrate:		EQU	24h	; 2: Keyboard repeat reat ; from mos_api.inc
sysvar_mouseButtons:	EQU	2Dh	; 1: Mouse button state ; from mos_api.inc
sysvar_mouseWheel:	EQU	2Eh	; 1: Mouse wheel delta ; from mos_api.inc
sysvar_mouseX:		EQU	29h	; 2: Mouse X position ; from mos_api.inc
sysvar_mouseXDelta:	EQU	2Fh	; 2: Mouse X delta ; from mos_api.inc
sysvar_mouseY:		EQU	2Bh	; 2: Mouse Y position ; from mos_api.inc
sysvar_mouseYDelta:	EQU	31h	; 2: Mouse Y delta ; from mos_api.inc
sysvar_rtc:		EQU	1Ah	; 6: Real time clock data ; from mos_api.inc
sysvar_rtcEnable:	EQU	28h	; 1: RTC enable flag (0: disabled, 1: use ESP32 RTC) ; from mos_api.inc
sysvar_scrColours:	EQU	15h	; 1: Number of colours displayed ; from mos_api.inc
sysvar_scrCols:		EQU	13h	; 1: Screen columns in characters ; from mos_api.inc
sysvar_scrHeight:	EQU	11h	; 2: Screen height in pixels ; from mos_api.inc
sysvar_scrMode:		EQU	27h	; 1: Screen mode ; from mos_api.inc
sysvar_scrRows:		EQU	14h	; 1: Screen rows in characters ; from mos_api.inc
sysvar_scrWidth:	EQU	0Fh	; 2: Screen width in pixels ; from mos_api.inc
sysvar_scrchar:		EQU	09h	; 1: Character read from screen ; from mos_api.inc
sysvar_scrpixel:	EQU	0Ah	; 3: Pixel data read from screen (R,B,G) ; from mos_api.inc
sysvar_scrpixelIndex:	EQU	16h	; 1: Index of pixel data read from screen ; from mos_api.inc
sysvar_spare:		EQU	20h	; 2: Spare, previously used by rtc ; from mos_api.inc
sysvar_time:		EQU	00h	; 4: Clock timer in centiseconds (incremented by 2 every VBLANK) ; from mos_api.inc
sysvar_vkeycode:	EQU	17h	; 1: Virtual key code from FabGL ; from mos_api.inc
sysvar_vkeycount:	EQU	19h	; 1: Incremented every time a key packet is received ; from mos_api.inc
sysvar_vkeydown:	EQU	18h	; 1: Virtual key state from FabGL (0=up, 1=down) ; from mos_api.inc
sysvar_vpd_pflags:	EQU	04h	; 1: Flags to indicate completion of VDP commands ; from mos_api.inc
vdp_audio:		EQU	85h ; from mos_api.inc
vdp_cursor:		EQU	82h ; from mos_api.inc
vdp_gp:			EQU 	80h ; from mos_api.inc
vdp_keycode:		EQU 	81h ; from mos_api.inc
vdp_keystate:		EQU	88h ; from mos_api.inc
vdp_logicalcoords:	EQU	C0h ; from mos_api.inc
vdp_mode:		EQU	86h ; from mos_api.inc
vdp_pflag_audio:	EQU	00001000b ; from mos_api.inc
vdp_pflag_cursor:	EQU	00000001b ; from mos_api.inc
vdp_pflag_mode:		EQU	00010000b ; from mos_api.inc
vdp_pflag_mouse:	EQU	01000000b ; from mos_api.inc
vdp_pflag_point:	EQU	00000100b ; from mos_api.inc
vdp_pflag_rtc:		EQU	00100000b ; from mos_api.inc
vdp_pflag_scrchar:	EQU	00000010b ; from mos_api.inc
vdp_rtc:		EQU	87h ; from mos_api.inc
vdp_scrchar:		EQU	83h ; from mos_api.inc
vdp_scrpixel:		EQU	84h ; from mos_api.inc
vdp_terminalmode:	EQU	FFh ; from mos_api.inc

; Macros

MACRO ADD8U_DE ; from macros.inc
			MACRO ADD8U_DE	reg
			ADD	A, E
			LD	E, A
			ADC	A, D
			SUB	E
			LD	D, A
			ENDMACRO

MACRO ADD8U_HL ; from macros.inc
			MACRO ADD8U_HL	reg
			ADD	A, L
			LD	L, A
			ADC	A, H
			SUB	L
			LD	H, A
			ENDMACRO

MACRO EXREG ; from macros.inc
			MACRO EXREG	rp1, rp2
			PUSH	rp1
			POP	rp2
			ENDMACRO

MACRO MOSCALL ; from mos_api.inc
			MACRO	MOSCALL function
			LD	A, function
			RST.L	08h
			ENDMACRO

MACRO RES_GPIO ; from macros.inc
			MACRO RES_GPIO	reg, val
			PUSH	BC
			LD	A, val
			CPL
			LD	C, A
			IN0	A, (reg)
			AND	C
			OUT0	(reg), A
			POP	BC
			ENDMACRO

MACRO SET_GPIO ; from macros.inc
			MACRO SET_GPIO	reg, val
			IN0	A, (reg)
			OR	val
			OUT0	(reg), A
			ENDMACRO

MACRO VDU ; from macros.inc
			MACRO VDU	val
			LD	A, val
			CALL	OSWRCH
			ENDMACRO

; Address Labels
ABSV: ; from eval.asm
ABSV: ; from fpp.asm
ACCS: ; from ram.asm
ACS: ; from eval.asm
ACS: ; from fpp.asm
ACS1: ; from fpp.asm
ADD1: ; from eval.asm
ADD1: ; from fpp.asm
ADDR16: ; from exec.asm
ADDR24: ; from exec.asm
ADDR_: ; from exec.asm
ADD_: ; from fpp.asm
ADL_: ; from exec.asm
ADVAL: ; from sorry.asm
ARGERR: ; from exec.asm
ARGUE: ; from exec.asm
ARGUE1: ; from exec.asm
ARGUE2: ; from exec.asm
ARGUE4: ; from exec.asm
ARGUE5: ; from exec.asm
ARGUE6: ; from exec.asm
ARGUE7: ; from exec.asm
ASC: ; from eval.asm
ASC0: ; from eval.asm
ASC1: ; from eval.asm
ASM: ; from exec.asm
ASM0: ; from exec.asm
ASMB: ; from exec.asm
ASMB1: ; from exec.asm
ASN: ; from eval.asm
ASN: ; from fpp.asm
ASSEM: ; from exec.asm
ASSEM0: ; from exec.asm
ASSEM1: ; from exec.asm
ASSEM2: ; from exec.asm
ASSEM3: ; from exec.asm
ASSEM4: ; from exec.asm
ASSEM5: ; from exec.asm
ASSIGN: ; from exec.asm
ATN: ; from eval.asm
ATN: ; from fpp.asm
ATN0: ; from fpp.asm
ATN1: ; from fpp.asm
ATN2: ; from fpp.asm
AUTONO: ; from ram.asm
BAD: ; from fpp.asm
BADBIN: ; from eval.asm
BADDIM: ; from exec.asm
BADHEX: ; from eval.asm
BGET: ; from eval.asm
BIN: ; from eval.asm
BIN1: ; from eval.asm
BIND: ; from exec.asm
BIND1: ; from exec.asm
BINDIG: ; from eval.asm
BITLOOKUP: ; from eval.asm
BIT_: ; from exec.asm
BPUT: ; from exec.asm
BRAKET: ; from eval.asm
BUFFER: ; from ram.asm
BYTE0: ; from exec.asm
BYTE_: ; from exec.asm
CALL1: ; from exec.asm
CALL2: ; from exec.asm
CALL_: ; from exec.asm
CB: ; from exec.asm
CHAIN: ; from exec.asm
CHAIN0: ; from exec.asm
CHANEL: ; from exec.asm
CHECK: ; from exec.asm
CHKO1: ; from fpp.asm
CHKO2: ; from fpp.asm
CHKOVF: ; from fpp.asm
CHNL: ; from exec.asm
CHRS: ; from eval.asm
CLI: ; from exec.asm
CLOSE: ; from exec.asm
CLR: ; from exec.asm
CLS: ; from exec.asm
CMDTAB: ; from exec.asm
COMDS: ; from patch.asm
COMMA: ; from eval.asm
CON: ; from eval.asm
CON: ; from fpp.asm
CON0: ; from fpp.asm
CON2: ; from fpp.asm
CON3: ; from fpp.asm
COND_: ; from exec.asm
CONS: ; from eval.asm
CONS1: ; from eval.asm
CONS2: ; from eval.asm
CONS3: ; from eval.asm
COPY0: ; from fpp.asm
COPY_: ; from fpp.asm
CORN: ; from exec.asm
COS: ; from eval.asm
COS: ; from fpp.asm
COS0: ; from fpp.asm
COUNT: ; from ram.asm
COUNT0: ; from eval.asm
COUNT1: ; from eval.asm
COUNT2: ; from eval.asm
COUNTV: ; from eval.asm
D2: ; from fpp.asm
D2C: ; from fpp.asm
DATPTR: ; from ram.asm
DB_: ; from exec.asm
DECODE: ; from eval.asm
DEFS: ; from exec.asm
DEG: ; from eval.asm
DEG: ; from fpp.asm
DELIM: ; from exec.asm
DIGITQ: ; from fpp.asm
DIM: ; from exec.asm
DIM1: ; from exec.asm
DIM2: ; from exec.asm
DIM3: ; from exec.asm
DIM4: ; from exec.asm
DIM5: ; from exec.asm
DISPAT: ; from eval.asm
DISPAT: ; from fpp.asm
DISPT0: ; from eval.asm
DISPT2: ; from eval.asm
DIV0: ; from fpp.asm
DIV1: ; from fpp.asm
DIV2: ; from fpp.asm
DIVA: ; from fpp.asm
DIVB: ; from fpp.asm
DIVC: ; from fpp.asm
DLOAD5: ; from fpp.asm
DLOAD5_SPL: ; from fpp.asm
DOIT: ; from eval.asm
DONE: ; from fpp.asm
DOSPC: ; from exec.asm
DOT: ; from exec.asm
DOTAB: ; from exec.asm
DOTAB1: ; from exec.asm
DO_KEYBOARD: ; from interrupts.asm
DO_KEYBOARD_0: ; from interrupts.asm
DO_KEYBOARD_1: ; from interrupts.asm
DTABLE: ; from fpp.asm
DYNVAR: ; from ram.asm
ED: ; from exec.asm
ENDPRO: ; from exec.asm
END_: ; from exec.asm
ENVEL: ; from sorry.asm
EOF: ; from eval.asm
EQUALS: ; from exec.asm
ERL: ; from ram.asm
ERLV: ; from eval.asm
ERR: ; from ram.asm
ERRLIN: ; from ram.asm
ERROR0: ; from eval.asm
ERROR0: ; from exec.asm
ERROR1: ; from eval.asm
ERROR1: ; from exec.asm
ERROR2: ; from exec.asm
ERROR3: ; from exec.asm
ERROR4: ; from exec.asm
ERROR_: ; from fpp.asm
ERRTRP: ; from ram.asm
ERRTXT: ; from ram.asm
ERRV: ; from eval.asm
ESCAPE: ; from exec.asm
ESCDIS: ; from patch.asm
ESCSET: ; from patch.asm
ESCTEST: ; from patch.asm
EVAL_: ; from eval.asm
EXIT_: ; from exec.asm
EXIT_: ; from fpp.asm
EXP: ; from eval.asm
EXP: ; from fpp.asm
EXP0: ; from fpp.asm
EXP1: ; from fpp.asm
EXP2: ; from fpp.asm
EXP3: ; from fpp.asm
EXP3S3: ; from eval.asm
EXP4: ; from fpp.asm
EXPR: ; from eval.asm
EXPR0A: ; from eval.asm
EXPR0B: ; from eval.asm
EXPR1: ; from eval.asm
EXPR1A: ; from eval.asm
EXPR2: ; from eval.asm
EXPR2B: ; from eval.asm
EXPR2C: ; from eval.asm
EXPR2S: ; from eval.asm
EXPR3: ; from eval.asm
EXPR3A: ; from eval.asm
EXPR3B: ; from eval.asm
EXPR3S: ; from eval.asm
EXPR4: ; from eval.asm
EXPR4A: ; from eval.asm
EXPR4B: ; from eval.asm
EXPR5: ; from eval.asm
EXPR5A: ; from eval.asm
EXPRI: ; from eval.asm
EXPRN: ; from eval.asm
EXPRS: ; from eval.asm
EXPRSC: ; from eval.asm
EXPR_W2: ; from patch.asm
EXT: ; from eval.asm
EXT: ; from exec.asm
EXT_DEFAULT: ; from patch.asm
EXT_HANDLER: ; from patch.asm
EXT_HANDLER_1: ; from patch.asm
EXT_HANDLER_2: ; from patch.asm
EXT_LOOKUP: ; from patch.asm
EZ80SFS_1: ; from exec.asm
EZ80SFS_2: ; from exec.asm
EZ80SFS_ADL0: ; from exec.asm
EZ80SFS_ADL1: ; from exec.asm
EZ80SF_FULL: ; from exec.asm
EZ80SF_OK: ; from exec.asm
EZ80SF_PART: ; from exec.asm
EZ80SF_TABLE: ; from exec.asm
FADD: ; from fpp.asm
FADD3: ; from fpp.asm
FADD4: ; from fpp.asm
FAND: ; from fpp.asm
FBDIV: ; from fpp.asm
FCOMP: ; from fpp.asm
FCOMP0: ; from fpp.asm
FCOMP1: ; from fpp.asm
FCP: ; from fpp.asm
FCP0: ; from fpp.asm
FCP1: ; from fpp.asm
FDIV: ; from fpp.asm
FEOR: ; from fpp.asm
FEQ: ; from fpp.asm
FETCHS: ; from exec.asm
FGE: ; from fpp.asm
FGT: ; from fpp.asm
FILL: ; from exec.asm
FILL1: ; from exec.asm
FIND: ; from exec.asm
FIND0: ; from exec.asm
FIND1: ; from exec.asm
FIND2: ; from exec.asm
FIND3: ; from exec.asm
FIND4: ; from exec.asm
FIND5: ; from exec.asm
FIND6: ; from exec.asm
FIX: ; from fpp.asm
FIX1: ; from fpp.asm
FIX2: ; from fpp.asm
FLAGS: ; from ram.asm
FLE: ; from fpp.asm
FLO48: ; from fpp.asm
FLOAT2: ; from fpp.asm
FLOATA: ; from fpp.asm
FLOAT_: ; from fpp.asm
FLT: ; from fpp.asm
FMOD: ; from fpp.asm
FMUL: ; from fpp.asm
FN: ; from exec.asm
FNCHK:			EQU     $			; This will never fall through as PROC1 will do a JP XEQ ; from exec.asm
FNE: ; from fpp.asm
FNEND: ; from exec.asm
FNEND0: ; from exec.asm
FNEND1: ; from exec.asm
FNEND5: ; from exec.asm
FNPTR: ; from ram.asm
FONE: ; from fpp.asm
FOR: ; from eval.asm
FOR: ; from exec.asm
FOR: ; from fpp.asm
FOR1: ; from exec.asm
FORCHK:			EQU     $ ; from exec.asm
FORMAT: ; from exec.asm
FORVAR: ; from exec.asm
FOR_: ; from fpp.asm
FPI180: ; from fpp.asm
FPOW: ; from fpp.asm
FPOW0: ; from fpp.asm
FPOW1: ; from fpp.asm
FPP: ; from fpp.asm
FPP1: ; from eval.asm
FPPN: ; from eval.asm
FREE: ; from ram.asm
FSUB: ; from fpp.asm
FTABLE: ; from fpp.asm
FTEST: ; from fpp.asm
FUNTBL: ; from eval.asm
FUNTBL_END:		EQU	$ ; from eval.asm
G9: ; from eval.asm
GET: ; from eval.asm
GET0: ; from eval.asm
GET1: ; from eval.asm
GETCSR: ; from patch.asm
GETDAT: ; from exec.asm
GETEX1: ; from fpp.asm
GETEX2: ; from fpp.asm
GETEXP: ; from fpp.asm
GETEXT: ; from patch.asm
GETIME: ; from patch.asm
GETIMS: ; from patch.asm
GETPTR: ; from patch.asm
GETS: ; from eval.asm
GOSCHK:			EQU     $ ; from exec.asm
GOSUB: ; from exec.asm
GOSUB1: ; from exec.asm
GOTO: ; from exec.asm
GOTO1: ; from exec.asm
GOTO2: ; from exec.asm
GPIOB_M0: ; from gpio.asm
GPIOB_M1: ; from gpio.asm
GPIOB_M2: ; from gpio.asm
GPIOB_M3: ; from gpio.asm
GPIOB_M4: ; from gpio.asm
GPIOB_M5: ; from gpio.asm
GPIOB_M6: ; from gpio.asm
GPIOB_M7: ; from gpio.asm
GPIOB_M8: ; from gpio.asm
GPIOB_M9: ; from gpio.asm
GPIOB_SETMODE: ; from gpio.asm
GROUP02: ; from exec.asm
GROUP04: ; from exec.asm
GROUP04_1: ; from exec.asm
GROUP05: ; from exec.asm
GROUP05_1: ; from exec.asm
GROUP05_HL: ; from exec.asm
GROUP07: ; from exec.asm
GROUP08: ; from exec.asm
GROUP09: ; from exec.asm
GROUP11: ; from exec.asm
GROUP12: ; from exec.asm
GROUP12_1: ; from exec.asm
GROUP13: ; from exec.asm
GROUP13_1: ; from exec.asm
GROUP14: ; from exec.asm
GROUP15: ; from exec.asm
GROUP15_1: ; from exec.asm
GROUP16: ; from exec.asm
GROUP17: ; from exec.asm
GROUP17_1: ; from exec.asm
HEX: ; from eval.asm
HEX: ; from exec.asm
HEX1: ; from eval.asm
HEX2: ; from eval.asm
HEXDIG: ; from eval.asm
HEXOUT: ; from exec.asm
HEXSP: ; from exec.asm
HEXST1: ; from eval.asm
HEXST2: ; from eval.asm
HEXST3: ; from eval.asm
HEXSTR: ; from eval.asm
HEXSTS: ; from eval.asm
HIMEM: ; from ram.asm
HIMEMV: ; from eval.asm
HIMEMV: ; from exec.asm
HUH: ; from patch.asm
IADD: ; from fpp.asm
IAND: ; from fpp.asm
IBDIV: ; from fpp.asm
ICP: ; from fpp.asm
ICP0: ; from fpp.asm
ICP1: ; from fpp.asm
IDIV: ; from fpp.asm
IEOR: ; from fpp.asm
IEQ: ; from fpp.asm
IEQ1: ; from fpp.asm
IF1: ; from exec.asm
IFNOT: ; from exec.asm
IF_: ; from exec.asm
IGE: ; from fpp.asm
IGE1: ; from fpp.asm
IGT: ; from fpp.asm
IGT1: ; from fpp.asm
ILE: ; from fpp.asm
ILE1: ; from fpp.asm
ILT: ; from fpp.asm
ILT1: ; from fpp.asm
IMOD: ; from fpp.asm
IMUL: ; from fpp.asm
IMUL1: ; from fpp.asm
INCC: ; from fpp.asm
INCREM: ; from ram.asm
INE: ; from fpp.asm
INE1: ; from fpp.asm
INKEY: ; from eval.asm
INKEY0: ; from eval.asm
INKEY1: ; from eval.asm
INKEYM: ; from eval.asm
INKEYS: ; from eval.asm
INPN1: ; from exec.asm
INPN2: ; from exec.asm
INPN3: ; from exec.asm
INPN4: ; from exec.asm
INPUT: ; from exec.asm
INPUT0: ; from exec.asm
INPUT1: ; from exec.asm
INPUT2: ; from exec.asm
INPUT3: ; from exec.asm
INPUT4: ; from exec.asm
INPUT5: ; from exec.asm
INPUT6: ; from exec.asm
INPUT9: ; from exec.asm
INPUTN: ; from exec.asm
INSTR: ; from eval.asm
INSTR1: ; from eval.asm
INSTR2: ; from eval.asm
INT_: ; from eval.asm
INT_: ; from fpp.asm
IOR: ; from fpp.asm
IPOW: ; from fpp.asm
IPOW0: ; from fpp.asm
IPOW1: ; from fpp.asm
IPOW2: ; from fpp.asm
IPOW3: ; from fpp.asm
IPOW4: ; from fpp.asm
IPOW5: ; from fpp.asm
ISUB: ; from fpp.asm
ITEM: ; from eval.asm
ITEM1: ; from eval.asm
ITEM2: ; from eval.asm
ITEMI: ; from eval.asm
ITEMN: ; from eval.asm
ITEMS: ; from eval.asm
KEYASCII: ; from ram.asm
KEYCOUNT: ; from ram.asm
KEYDOWN: ; from ram.asm
LD16: ; from exec.asm
LD8: ; from exec.asm
LDA: ; from exec.asm
LDIN: ; from exec.asm
LDOP: ; from exec.asm
LDOPS: ; from exec.asm
LEFT1: ; from eval.asm
LEFT2: ; from eval.asm
LEFT3: ; from eval.asm
LEFTS: ; from eval.asm
LEN: ; from eval.asm
LET: ; from exec.asm
LET0: ; from exec.asm
LINE1S: ; from exec.asm
LINENO: ; from ram.asm
LINES: ; from exec.asm
LISTON: ; from ram.asm
LN: ; from eval.asm
LN: ; from fpp.asm
LN0: ; from fpp.asm
LN1: ; from fpp.asm
LN2: ; from fpp.asm
LN3: ; from fpp.asm
LN4: ; from fpp.asm
LOAD1: ; from eval.asm
LOAD4: ; from eval.asm
LOAD5: ; from eval.asm
LOADN: ; from eval.asm
LOADS: ; from eval.asm
LOADS2: ; from eval.asm
LOCAL1: ; from exec.asm
LOCAL2: ; from exec.asm
LOCAL_: ; from exec.asm
LOCCHK:			EQU     $ ; from exec.asm
LOG: ; from eval.asm
LOG: ; from fpp.asm
LOMEM: ; from ram.asm
LOMEMV: ; from eval.asm
LOMEMV: ; from exec.asm
LOOP_: ; from exec.asm
LTRAP: ; from patch.asm
LTRAP1: ; from patch.asm
MIDS: ; from eval.asm
MIDS1: ; from eval.asm
MINUS: ; from eval.asm
MINUS0: ; from eval.asm
MOD48: ; from fpp.asm
MOD481: ; from fpp.asm
MOD482: ; from fpp.asm
MOD483: ; from fpp.asm
MOD484: ; from fpp.asm
MOD485: ; from fpp.asm
MUL0: ; from fpp.asm
MUL1: ; from fpp.asm
MUL16: ; from exec.asm
MULA: ; from fpp.asm
MULB: ; from fpp.asm
NEG0: ; from fpp.asm
NEGATE: ; from eval.asm
NEGATE: ; from fpp.asm
NEG_: ; from fpp.asm
NEWLIN: ; from exec.asm
NEXT: ; from exec.asm
NEXT0: ; from exec.asm
NEXT1: ; from exec.asm
NOROOM: ; from exec.asm
NOS1: ; from eval.asm
NOSUCH: ; from eval.asm
NOTK: ; from eval.asm
NOTK: ; from fpp.asm
NUMB1: ; from fpp.asm
NUMBER: ; from exec.asm
NUMBER: ; from fpp.asm
NUMBIX: ; from fpp.asm
NXT: ; from eval.asm
ODD: ; from fpp.asm
OFFSET: ; from exec.asm
OFLOW: ; from fpp.asm
ON1: ; from exec.asm
ON2: ; from exec.asm
ON3: ; from exec.asm
ON4: ; from exec.asm
ONERR: ; from exec.asm
ONPROC: ; from exec.asm
ON_: ; from exec.asm
OP: ; from fpp.asm
OPCODS: ; from exec.asm
OPENIN: ; from eval.asm
OPENIN_1: ; from eval.asm
OPENOT: ; from eval.asm
OPENUP: ; from eval.asm
OPND: ; from exec.asm
OPRNDS: ; from exec.asm
OPT: ; from exec.asm
OPTS: ; from exec.asm
ORC: ; from exec.asm
OSBGET: ; from patch.asm
OSBPUT: ; from patch.asm
OSBYTE: ; from patch.asm
OSBYTE_0B: ; from patch.asm
OSBYTE_0C: ; from patch.asm
OSBYTE_13: ; from patch.asm
OSBYTE_76: ; from patch.asm
OSBYTE_A0: ; from patch.asm
OSCALL: ; from patch.asm
OSCALL_1: ; from patch.asm
OSCALL_2: ; from patch.asm
OSCALL_TABLE: ; from patch.asm
OSCLI: ; from patch.asm
OSCLI0: ; from patch.asm
OSCLI1: ; from patch.asm
OSCLI2: ; from patch.asm
OSCLI3: ; from patch.asm
OSCLI4: ; from patch.asm
OSCLI5: ; from patch.asm
OSCLI6: ; from patch.asm
OSERROR: ; from patch.asm
OSINIT: ; from patch.asm
OSKEY: ; from patch.asm
OSLINE: ; from patch.asm
OSLINE1: ; from patch.asm
OSLOAD: ; from patch.asm
OSLOAD_BBC: ; from patch.asm
OSLOAD_TXT: ; from patch.asm
OSLOAD_TXT1: ; from patch.asm
OSLOAD_TXT2: ; from patch.asm
OSLOAD_TXT3: ; from patch.asm
OSLOAD_TXT4: ; from patch.asm
OSOPEN: ; from patch.asm
OSRDCH: ; from patch.asm
OSSAVE: ; from patch.asm
OSSAVE_BBC: ; from patch.asm
OSSAVE_TXT: ; from patch.asm
OSSAVE_TXT1: ; from patch.asm
OSSAVE_TXT2: ; from patch.asm
OSSHUT: ; from patch.asm
OSSTAT: ; from patch.asm
OSWRCH: ; from patch.asm
OSWRCHCH: ; from ram.asm
OSWRCHFH: ; from ram.asm
OSWRCHPT: ; from ram.asm
OSWRCH_BUFFER: ; from patch.asm
OSWRCH_FILE: ; from patch.asm
OUTCH1: ; from exec.asm
PAGEV: ; from eval.asm
PAGEV: ; from exec.asm
PAGE_: ; from ram.asm
PAIR: ; from exec.asm
PAIR1: ; from exec.asm
PI: ; from eval.asm
PI: ; from fpp.asm
PIBY4: ; from fpp.asm
POLY: ; from fpp.asm
POLY1: ; from fpp.asm
POP5: ; from fpp.asm
POPS: ; from eval.asm
POPS1: ; from eval.asm
POS: ; from eval.asm
POWR10: ; from fpp.asm
POWR11: ; from fpp.asm
POWR12: ; from fpp.asm
POWR13: ; from fpp.asm
POWR14: ; from fpp.asm
PRINT0: ; from exec.asm
PRINT3: ; from exec.asm
PRINT4: ; from exec.asm
PRINT6: ; from exec.asm
PRINT8: ; from exec.asm
PRINT9: ; from exec.asm
PRINTA: ; from exec.asm
PRINTC: ; from exec.asm
PRINT_: ; from exec.asm
PRNTN1: ; from exec.asm
PRNTN2: ; from exec.asm
PRNTN3: ; from exec.asm
PRNTN4: ; from exec.asm
PROC: ; from exec.asm
PROC1: ; from exec.asm
PROC2: ; from exec.asm
PROC3: ; from exec.asm
PROC4: ; from exec.asm
PROC5: ; from exec.asm
PROC6: ; from exec.asm
PROCHK:			EQU     $			; This will never fall through as PROC1 will do a JP XEQ ; from exec.asm
PROMPT: ; from patch.asm
PROPTR: ; from ram.asm
PTEXT: ; from exec.asm
PTEXT1: ; from exec.asm
PTR: ; from eval.asm
PTR: ; from exec.asm
PUSH5: ; from fpp.asm
PUSHS: ; from eval.asm
PUSHS1: ; from eval.asm
PUT: ; from exec.asm
PUTCSR: ; from patch.asm
PUTIME: ; from patch.asm
PUTIMS: ; from sorry.asm
PUTPTR: ; from patch.asm
R0: ; from ram.asm
R1: ; from ram.asm
RAD: ; from eval.asm
RAD: ; from fpp.asm
RAM_END: ; from ram.asm
RAM_START: ; from ram.asm
RANDOM: ; from ram.asm
RATIO: ; from fpp.asm
RDIV: ; from fpp.asm
READ: ; from exec.asm
READ0: ; from exec.asm
READ1: ; from exec.asm
READ2: ; from exec.asm
READKEY: ; from patch.asm
RECIP: ; from fpp.asm
REFIL0: ; from exec.asm
REFIL1: ; from exec.asm
REFILL: ; from exec.asm
REG: ; from exec.asm
REGHI: ; from exec.asm
REGLO: ; from exec.asm
REM: ; from exec.asm
REPCHK:			EQU     $ ; from exec.asm
REPEAT: ; from exec.asm
REPOR: ; from exec.asm
RESET: ; from patch.asm
RESTOR: ; from exec.asm
RESTR1: ; from exec.asm
RETURN: ; from exec.asm
RIGHT1: ; from eval.asm
RIGHTS: ; from eval.asm
RND: ; from eval.asm
RND1: ; from eval.asm
RND2: ; from eval.asm
RND3: ; from eval.asm
RND4: ; from eval.asm
RND5: ; from eval.asm
RND6: ; from eval.asm
RND7: ; from eval.asm
RSUB: ; from fpp.asm
RTABLE: ; from fpp.asm
RUN: ; from exec.asm
RUN0: ; from exec.asm
SAVE: ; from eval.asm
SAVE1: ; from eval.asm
SAVLO1: ; from exec.asm
SAVLO2: ; from exec.asm
SAVLO4: ; from exec.asm
SAVLO5: ; from exec.asm
SAVLOC: ; from exec.asm
SCALE: ; from fpp.asm
SCP: ; from eval.asm
SCP0: ; from eval.asm
SCP1: ; from eval.asm
SCP2: ; from eval.asm
SCP3: ; from eval.asm
SEARCH: ; from eval.asm
SEARCH: ; from exec.asm
SEQ: ; from eval.asm
SFIX: ; from eval.asm
SFIX: ; from fpp.asm
SFLOAT: ; from eval.asm
SFLOAT: ; from fpp.asm
SGE: ; from eval.asm
SGN: ; from eval.asm
SGN: ; from fpp.asm
SGT: ; from eval.asm
SHL3: ; from exec.asm
SIGN: ; from exec.asm
SIGNQ: ; from fpp.asm
SIN: ; from eval.asm
SIN: ; from fpp.asm
SIN0: ; from fpp.asm
SIN1: ; from fpp.asm
SIN2: ; from fpp.asm
SIN3: ; from fpp.asm
SKIP: ; from exec.asm
SKIP0: ; from exec.asm
SKIPSP: ; from patch.asm
SLE: ; from eval.asm
SLT: ; from eval.asm
SNE: ; from eval.asm
SOPTBL: ; from eval.asm
SPAN: ; from exec.asm
SQR: ; from eval.asm
SQR: ; from fpp.asm
SQR0: ; from fpp.asm
SQR1: ; from fpp.asm
SQR2: ; from fpp.asm
SQR3: ; from fpp.asm
SQRA: ; from fpp.asm
SQRB: ; from fpp.asm
SQUARE: ; from fpp.asm
SRCH1: ; from eval.asm
SRCH1: ; from exec.asm
SRCH2: ; from eval.asm
SRCH2: ; from exec.asm
SRCH3: ; from eval.asm
SRCH4: ; from eval.asm
STACCS: ; from exec.asm
STAR_ASM: ; from patch.asm
STAR_BYE: ; from patch.asm
STAR_EDIT: ; from patch.asm
STAR_FX: ; from patch.asm
STAR_FX1: ; from patch.asm
STAR_FX2: ; from patch.asm
STAR_VERSION: ; from patch.asm
STAVAR: ; from ram.asm
STOP: ; from exec.asm
STORE: ; from exec.asm
STORE1: ; from exec.asm
STORE4: ; from exec.asm
STORE5: ; from exec.asm
STOREI: ; from exec.asm
STORES: ; from exec.asm
STORS1: ; from exec.asm
STORS3: ; from exec.asm
STORS5: ; from exec.asm
STR: ; from eval.asm
STR: ; from fpp.asm
STR0: ; from eval.asm
STR1: ; from eval.asm
STR10: ; from fpp.asm
STR11: ; from fpp.asm
STR13: ; from fpp.asm
STR14: ; from fpp.asm
STR15: ; from fpp.asm
STR2: ; from eval.asm
STR2: ; from fpp.asm
STR20: ; from fpp.asm
STR21: ; from fpp.asm
STR22: ; from fpp.asm
STR23: ; from fpp.asm
STR24: ; from fpp.asm
STR25: ; from fpp.asm
STR26: ; from fpp.asm
STR27: ; from fpp.asm
STR3: ; from fpp.asm
STR30: ; from fpp.asm
STR31: ; from fpp.asm
STR32: ; from fpp.asm
STR33: ; from fpp.asm
STR34: ; from fpp.asm
STR35: ; from fpp.asm
STR36: ; from fpp.asm
STR37: ; from fpp.asm
STR38: ; from fpp.asm
STR39: ; from fpp.asm
STR3A: ; from fpp.asm
STR4: ; from fpp.asm
STR40: ; from fpp.asm
STR41: ; from fpp.asm
STR42: ; from fpp.asm
STR43: ; from fpp.asm
STR44: ; from fpp.asm
STR47: ; from fpp.asm
STRIN1: ; from eval.asm
STRIN2: ; from eval.asm
STRING_: ; from eval.asm
STRS: ; from eval.asm
SUB_: ; from fpp.asm
SWAP: ; from eval.asm
SWAP: ; from fpp.asm
SWAP1: ; from fpp.asm
SYNTAX: ; from exec.asm
TABIT: ; from exec.asm
TAN: ; from eval.asm
TAN: ; from fpp.asm
TERM: ; from exec.asm
TERM0: ; from exec.asm
TERMQ: ; from exec.asm
TEST: ; from eval.asm
TEST: ; from fpp.asm
TIME0: ; from eval.asm
TIMEV: ; from eval.asm
TIMEV: ; from exec.asm
TIMEVS: ; from eval.asm
TIMEVS: ; from exec.asm
TOOFAR: ; from exec.asm
TOP: ; from ram.asm
TOPV: ; from eval.asm
TRACE: ; from exec.asm
TRACE0: ; from exec.asm
TRACE1: ; from exec.asm
TRACEN: ; from ram.asm
TRAP: ; from patch.asm
TYPE_: ; from eval.asm
UNSTK: ; from exec.asm
UNSTK1: ; from exec.asm
UNTIL: ; from exec.asm
UPPRC: ; from patch.asm
USER: ; from ram.asm
USR: ; from exec.asm
USR1: ; from exec.asm
USR2: ; from exec.asm
VAL: ; from eval.asm
VAL: ; from fpp.asm
VAL0: ; from eval.asm
VAL16: ; from exec.asm
VAL24: ; from exec.asm
VAL8: ; from exec.asm
VAR_: ; from exec.asm
VBLANK_HANDLER: ; from interrupts.asm
VBLANK_HANDLER_JP: ; from interrupts.asm
VBLANK_INIT: ; from interrupts.asm
VBLANK_STOP: ; from interrupts.asm
VDU: ; from exec.asm
VDU1: ; from exec.asm
VDU2: ; from exec.asm
VDU3: ; from exec.asm
VDU4: ; from exec.asm
VPOS: ; from eval.asm
WAIT_VBLANK: ; from patch.asm
WIDTH: ; from ram.asm
WIDTHV: ; from exec.asm
X10: ; from fpp.asm
X10B: ; from fpp.asm
X2: ; from fpp.asm
X4OR5: ; from exec.asm
X5: ; from fpp.asm
XEQ: ; from exec.asm
XEQ0: ; from exec.asm
XEQ1: ; from exec.asm
XEQ2: ; from exec.asm
XEQR: ; from exec.asm
XTRAC1: ; from exec.asm
XTRACT: ; from exec.asm
ZERO: ; from eval.asm
ZERO: ; from fpp.asm
_argv_ptrs: ; from init.asm
_clear_ram: ; from init.asm
_end: ; from init.asm
_exec_name: ; from init.asm
_get_token: ; from init.asm
_parse_params: ; from init.asm
_parse_params_1: ; from init.asm
_skip_spaces: ; from init.asm
_sps: ; from init.asm
_start: ; from init.asm
