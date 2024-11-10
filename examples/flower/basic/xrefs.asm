; ===== STUB FUNCTIONS =====
printInline:
    ret

ESCSET:
	call printInline
	asciz "interrupts.asm called ESCSET!"
	ret

