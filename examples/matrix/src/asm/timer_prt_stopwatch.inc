prt_stopwatch_reload: equ 72000/1000 ; 1 millisecond with clock divider 256

; set PRT timer
prt_stopwatch_set:
    ld hl,0
    ld (prt_stopwatch_irq_counter),hl
    
    ld hl,prt_stopwatch_reload
    out0 (TMR1_CTL+TMR_RES_LOW),l
	out0 (TMR1_CTL+TMR_RES_HIGH),h
; disable timer (in effect, reset it)
    ld a,PRT_IRQ_0 | IRQ_EN_0 | PRT_MODE_0 | CLK_DIV_256 | RST_EN_1 | PRT_EN_0
	out0 (TMR1_CTL+TMR_REG_CTL),a
; enable timer,with interrupt and CONTINUOUS mode,clock divider 256
    ld a,PRT_IRQ_0 | IRQ_EN_1 | PRT_MODE_1 | CLK_DIV_256 | RST_EN_1 | PRT_EN_1
	out0 (TMR1_CTL+TMR_REG_CTL),a
    ret

; get PRT stopwatch elapsed time in milliseconds
prt_stopwatch_get:
    ld hl,(prt_stopwatch_irq_counter)
    ret

; stop PRT timer
prt_stopwatch_stop:
    ld a,PRT_IRQ_0 | IRQ_EN_0 | PRT_MODE_0 | CLK_DIV_256 | RST_EN_1 | PRT_EN_0
	out0 (TMR1_CTL+TMR_REG_CTL),a
    ret

; ===============================================
; PRT Timer Interrupt Handling
; https://github.com/tomm/agon-cpu-emulator/blob/main/sdcard/regression_suite/timerirq.asm
; -----------------------------------------------
prt_stopwatch_irq_init:
    ; set up interrupt vector table 2
	ld hl,0
	ld a,($10c)
	ld l,a
	ld a,($10d)
	ld h,a

	; skip over CALL ($c3)
	inc hl
	; load address of jump into vector table 2 (in ram)
	ld hl,(hl)

	; write CALL prt_irq_handler to vector table 2
	ld a,$c3
	ld (hl),a
	inc hl
	ld de,prt_stopwatch_irq_handler
	ld (hl),de

    ret

prt_stopwatch_irq_handler:
	di
	push af
    push hl
	in0 a,(TMR1_CTL+TMR_REG_CTL)
	ld hl,(prt_stopwatch_irq_counter)
	inc hl
	ld (prt_stopwatch_irq_counter),hl
    pop hl
	pop af
	ei
	reti.l

prt_stopwatch_irq_counter:
	.dl 0
