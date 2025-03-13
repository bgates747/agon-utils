; https://agonconsole8.github.io/agon-docs/vdp/Buffered-Commands-API/

; Command 0: Write block to a buffer
; VDU 23, 0, &A0, bufferId; 0, length; <buffer-data>
; inputs: hl = bufferId, bc = length of data, de = pointer to data
vdu_write_block_to_buffer:
; back up input parameters
    push de ; pointer to data
    push bc ; length of data
; set up the vdu command string
    ld (@bufferId),hl
    ld (@length),bc
    xor a ; load buffer
    ld (@bufferId+2),a
    ld hl,@cmd0
    ld bc,@end0-@cmd0
    rst.lil $18
; send the buffer data
    pop bc ; length of data
    pop hl ; pointer to data (was de)
    rst.lil $18 ; send it
    ret
; command string data
@cmd0:      db 23,0,0xA0
@bufferId:	dw 0x0000
            db 0 ; load buffer
@length:	dw 0x0000
@end0:      db 0x00 ; padding
; end vdu_write_block_to_buffer

; Command 1: Call a buffer
; VDU 23, 0, &A0, bufferId; 1
; inputs: hl = bufferId
vdu_call_buffer:
    ld (@bufferId),hl
    ld a,1 ; call buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 1 ; call buffer
@end:
; end vdu_call_buffer

; Command 2: Clear a buffer
; VDU 23, 0 &A0, bufferId; 2
; inputs: hl = bufferId
vdu_clear_buffer:
    ld (@bufferId),hl
    ld a,2 ; clear buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 2 ; clear buffer
@end: 
; end vdu_clear_buffer

; Clear all buffers
; inputs: none
vdu_clear_all_buffers:
; clear all buffers
    ld hl,@beg
    ld bc,@end-@beg
    rst.lil $18
    ret
@beg: db 23,0,$A0
      dw -1 ; bufferId -1 (65535) means clear all buffers
      db 2  ; command 2: clear a buffer
@end:
; end vdu_clear_all_buffers

; Command 3: Create a writeable buffer
; VDU 23, 0 &A0, bufferId; 3, length;
; inputs: hl = bufferId, bc = length
vdu_create_writeable_buffer:
    ld (@bufferId),hl
    ld (@length),bc
    ld a,3 ; create writeable buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 3 ; create writeable buffer
@length: dw 0x0000
@end:     db 0x00 ; padding
; end vdu_create_writeable_buffer

; Command 4: Set output stream to a buffer
; VDU 23, 0 &A0, bufferId; 4
; inputs: hl = bufferId
vdu_set_output_stream_buffer:
    ld (@bufferId),hl
    ld a,4 ; set output stream to buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 4 ; set output stream to buffer
@end:     db 0x00 ; padding
; end vdu_set_output_stream_buffer

; Command 5: Adjust buffer contents
; VDU 23, 0, &A0, bufferId; 5, operation, offset; [count;] <operand>, [arguments]
vdu_adjust_buffer:
    ret ; TODO: implement
; end vdu_adjust_buffer

; Command 6: Conditionally call a buffer
; VDU 23, 0, &A0, bufferId; 6, operation, checkBufferId; checkOffset; [arguments]
vdu_call_buffer_conditional:
    ret ; TODO: implement
; end vdu_call_buffer_conditional

; Command 7: Jump to a buffer
; VDU 23, 0, &A0, bufferId; 7
; inputs: hl = bufferId
vdu_jump_to_buffer:
    ld (@bufferId),hl
    ld a,7 ; jump to buffer
    ld (@bufferId+2),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@bufferId: dw 0x0000
           db 7 ; jump to buffer
@end:     db 0x00 ; padding
; end vdu_jump_to_buffer

; Command 8: Conditional Jump to a buffer
; VDU 23, 0, &A0, bufferId; 8, operation, checkBufferId; checkOffset; [arguments]
vdu_jump_to_buffer_conditional:
    ret ; TODO: implement
; end vdu_jump_to_buffer_conditional

; Command 9: Jump to an offset in a buffer
; VDU 23, 0, &A0, bufferId; 9, offset; offsetHighByte, [blockNumber;]
vdu_jump_to_buffer_offset:
    ret ; TODO: implement
; end vdu_jump_to_buffer_offset

; Command 10: Conditional jump to an offset in a buffer
; VDU 23, 0, &A0, bufferId; 10, offset; offsetHighByte, [blockNumber;] [arguments]
vdu_jump_to_buffer_offset_conditional:
    ret ; TODO: implement
; end vdu_jump_to_buffer_offset_conditional

; Command 11: Call buffer with an offset
; VDU 23, 0, &A0, bufferId; 11, offset; offsetHighByte, [blockNumber;]
vdu_call_buffer_offset:
    ret ; TODO: implement
; end vdu_call_buffer_offset

; Command 23: Set affine transforms test flag
; VDU 23, 0, &F8, 1; 1;
; inputs: none
vdu_enable_transforms:
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:   db 23,0,0xF8
        dw 1 ; magic number
        dw 1 ; ditto
@end:
; end vdu_enable_transforms

; Command 32: Create or manipulate a 2D affine transformation matrix
; VDU 23, 0, &A0, bufferId; 32, operation, [<format>, <arguments...>] 
; inputs: a = operation, hl = bufferId, de = pointer to arguments, bc = length of arguments, ixl = format
vdu_do_2d_matrix_transform:
    push af ; save operation
    push bc ; length of arguments
    push de ; pointer to arguments
    ld (@operation),a
    ld a,l
    ld (@bufferId+0),a
    ld a,h
    ld (@bufferId+1),a
    ld a,ixl
    ld (@format),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop hl ; pointer to arguments (was de)
    pop bc ; length of arguments
    pop af ; restore operation
    cp 1 ; if > 1, send the arguments
    ret c ; no arguments
    rst.lil $18 ; send the arguments
    ret
@cmd:       db 23,0,0xA0
@bufferId:  dw 0x0000
            db 32 ; create transform matrix
@operation: db 0x00
@format:    db 0x00
@end:
; end vdu_do_2d_matrix_transform

; Command 33: Create or manipulate a 3D affine transformation matrix
; VDU 23, 0, &A0, bufferId; 33, operation, [<format>, <arguments...>]
; inputs: a = operation, hl = bufferId, de = pointer to arguments, bc = length of arguments, ixl = format
vdu_do_3d_matrix_transform:
    push af ; save operation
    push bc ; length of arguments
    push de ; pointer to arguments
    ld (@operation),a
    ld a,l
    ld (@bufferId+0),a
    ld a,h
    ld (@bufferId+1),a
    ld a,ixl
    ld (@format),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop hl ; pointer to arguments (was de)
    pop bc ; length of arguments
    pop af ; restore operation
    cp 1 ; if > 1, send the arguments
    ret c ; no arguments
    rst.lil $18 ; send the arguments
    ret
@cmd:       db 23,0,0xA0
@bufferId:  dw 0x0000
            db 33 ; manipulate transform matrix
@operation: db 0x00
@format:    db 0x00
@end:
; end vdu_do_3d_matrix_transform

; Command 40: Create a transformed bitmap
; VDU 23, 0, &A0, bufferId; 40, options, transformBufferId; sourceBitmapId; [width; height;]
; inputs a = options, de = bufferId, bc = transformBufferId, hl = sourceBitmapId, ix = width, iy = height
; options:
; Bit value Arguments       Description
; 1 		                Target bitmap should be resized. When not set, target will be same dimensions as the original bitmap.
; 2 	    width; height; 	Target bitmap will be resized to explicitly given dimensions
; 4 Automatically translate target bitmap position. When set the calculated transformed minimum x,y coordinates will be placed at the top left of the target
vdu_transform_bitmap:
    push af ; save options
    ld (@options),a
    ld a,e
    ld (@bufferId+0),a
    ld a,d
    ld (@bufferId+1),a
    ld (@transformBufferId),bc
    ld (@sourceBitmapId),hl
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    pop af ; restore options
    bit 2,a ; check resize bit
    ret z
    ld (@width),ix
    ld (@height),iy
    ld hl,@width
    ld bc,4
    rst.lil $18
    ret
@cmd:       db 23,0,0xA0
@bufferId:  dw 0x0000
            db 40 ; create transformed bitmap
@options:   db 0x00
@transformBufferId: dw 0x0000
@sourceBitmapId:    dw 0x0000
@end:       db 0x00 ; padding
; these are only included when bit 2 of options (resize) is set
@width:     dw 0x0000
@height:    dw 0x0000
            db 0x00 ; padding
; end vdu_transform_bitmap

; Command 64: Compress a buffer
; VDU 23, 0, &A0, targetBufferId; 64, sourceBufferId;
; inputs: hl = sourceBufferId, de = targetBufferId
vdu_compress_buffer:
    ld (@sourceBufferId),hl
    ld (@targetBufferId),de
    ld a,64 ; compress buffer
    ld (@sourceBufferId-1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@targetBufferId: dw 0x0000
           db 64 ; compress buffer
@sourceBufferId: dw 0x0000
@end:     db 0x00 ; padding


; Command 65: Decompress a buffer
; VDU 23, 0, &A0, targetBufferId; 65, sourceBufferId;
; inputs: hl = sourceBufferId, de = targetBufferId
vdu_decompress_buffer:
    ld (@sourceBufferId),hl
    ld (@targetBufferId),de
    ld a,65 ; decompress buffer
    ld (@sourceBufferId-1),a
    ld hl,@cmd
    ld bc,@end-@cmd
    rst.lil $18
    ret
@cmd:     db 23,0,0xA0
@targetBufferId: dw 0x0000
           db 65 ; decompress buffer
@sourceBufferId: dw 0x0000
@end:     db 0x00 ; padding