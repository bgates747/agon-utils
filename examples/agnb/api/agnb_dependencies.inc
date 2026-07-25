; Optional AGNB dependency reference
; ==================================
;
; DO NOT include this file wholesale when the application already provides
; any of these names. Copy or retain only the missing definitions. The public
; API is agnb_api.inc; this file merely collects the exact implementations used by
; the proven image and audio harnesses.

; FatFS call wrapper and minimal MOS definitions
    MACRO FFSCALL function
        push iy
        ld a,function
        rst.lil $08
        pop iy
    ENDMACRO

ffs_fopen:             equ $80
ffs_fclose:            equ $81
ffs_fread:             equ $82
fa_read:               equ $01
ffobjid_objsize:       equ 11
fil_obj:               equ 0
fil_dir_ptr:           equ 33

; Unsigned native-ADL multiply: HL = HL * DE. Preserves AF, BC, DE.
umul24:
    push de
    push bc
    push af
    push hl
    pop bc
    ld a,24
    ld hl,0
@loop:
    add hl,hl
    ex de,hl
    add hl,hl
    ex de,hl
    jr nc,@no_add
    add hl,bc
@no_add:
    dec a
    jr nz,@loop
    pop af
    pop bc
    pop de
    ret

; VDU buffer upload: HL=bufferId, BC=length, DE=data pointer.
vdu_load_buffer:
    ld (@length),bc
    push de
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop hl
    ld bc,(@length)
    rst.lil $18
    ret
@cmd:       db 23,0,$A0
@bufferId:  dw 0
            db 0
@length:    dw 0
@end:       db 0

; Clear HL=bufferId.
vdu_clear_buffer:
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:       db 23,0,$A0
@bufferId:  dw 0
            db 2
@end:

; Consolidate all blocks in HL=bufferId.
vdu_consolidate_buffer:
    ld a,l
    ld (@bufferId),a
    ld a,h
    ld (@bufferId+1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:       db 23,0,$A0
@bufferId:  dw 0
            db 14
@end:

; Select HL=bufferId as the current bitmap.
vdu_buff_select:
    ld (@bufferId),hl
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:       db 23,27,$20
@bufferId:  dw 0
@end:

; Create a bitmap from the selected buffer: A=format, BC=width, DE=height.
vdu_bmp_create:
    ld (@width),bc
    ld (@height),de
    ld (@format),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:       db 23,27,$21
@width:     dw 0
@height:    dw 0
@format:    db 0
@end:

; Convert a consolidated buffer to a sample.
; Inputs: HL=bufferId, A=base format (0 signed, 1 unsigned), DE=sample rate.
vdu_buffer_to_sound:
    ld (@bufferId),hl
    add a,8
    ld (@format),a
    ld (@sampleRate),de
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:        db 23,0,$85
             db 0,5,2
@bufferId:   dw 0
@format:     db 0
@sampleRate: dw 0
@end:
