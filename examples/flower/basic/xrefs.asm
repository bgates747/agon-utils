; ===== STUB FUNCTIONS =====
printInline:
    ret

EXTERR:
	call printInline
	asciz "sorry.asm called EXTERR!"
	ret
