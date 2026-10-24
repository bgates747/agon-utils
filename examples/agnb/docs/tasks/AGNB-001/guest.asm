; Actual MOS/VDP tests for the generic loader. Numeric observations only.
 .assume adl=1
 .org $40000
 jp start
 .align 64
 db "MOS",0,1
start:
 push af
 push bc
 push de
 push hl
 push ix
 push iy
 ld a,8
 rst.lil $08
 push ix
 pop iy
 ld hl,observations
 ld (cursor),hl
 ld hl,query_setup
 ld bc,query_setup_end-query_setup
 call send
 ld de,file0
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 ld de,file1
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 ld de,file2
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 ld de,file3
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 ld de,file4
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 ld de,file5
 ld hl,record_complete
 call agnb_load_buffers_with_callback
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl

 ld hl,(cursor)
 ld de,observations
 or a
 sbc hl,de
 push hl
 pop bc
 ld hl,result_name
 ld a,2
 rst.lil $08
 ld hl,message
 ld bc,message_end-message
 call send
 pop iy
 pop ix
 pop hl
 pop de
 pop bc
 pop af
 ld hl,0
 ret

record_complete:
 push af
 push bc
 push de
 push hl
 push ix
 push iy
 ld hl,(cursor)
 ld a,(agnb_metadata)
 ld (hl),a
 ld (copy_id),a
 inc hl
 ld a,(agnb_metadata+1)
 ld (hl),a
 ld (copy_id+1),a
 inc hl
 ld de,(agnb_metadata+7)
 ld (hl),de
 inc hl
 inc hl
 inc hl
 ld (cursor),hl
 call query_byte
 jr nc,record_byte_ok
 ld a,255
record_byte_ok:
 ld hl,(cursor)
 ld (hl),a
 inc hl
 ld (cursor),hl
 pop iy
 pop ix
 pop hl
 pop de
 pop bc
 pop af
 ret

send:
    push ix
    push iy
    xor a
    rst.lil 18h
    pop iy
    pop ix
    ret

query_byte:
    ld a,15
    ld (query_mask),a
    ld a,16
    ld (query_tag),a
    call query_nibble
    ret c
    and 15
    ld (low_nibble),a
    ld a,240
    ld (query_mask),a
    ld a,8
    ld (query_tag),a
    call query_nibble
    ret c
    and 240
    ld b,a
    ld a,(low_nibble)
    or b
    ret

query_nibble:
    ld a,255
    ld (iy+0x37),a
    ld hl,query_packet
    ld bc,query_end-query_packet
    call send
    ld a,(iy+0)
    ld d,a
wait_gp:
    ld a,(iy+0x37)
    cp 255
    jr nz,got_gp
    ld a,(iy+0)
    sub d
    cp 240
    jr c,wait_gp
    scf
    ret
got_gp:
    ld e,a
    ld a,(query_tag)
    cp 16
    ld a,e
    jr nz,check_high
    and 240
    cp 16
    jr check_tag
check_high:
    and 15
    cp 8
check_tag:
    jr nz,bad_tag
    ld a,e
    or a
    ret
bad_tag:
    scf
    ret

query_packet:
    db 23,0,160
    dw 60000
    db 5,2
    dw 3
    db 0x55
    db 23,0,160
    dw 60000
    db 5,0xe2
    dw 3,1
copy_id: dw 0
copy_offset: dw 0
    db 23,0,160
    dw 60000
    db 5,5
    dw 3
query_mask: db 15
    db 23,0,160
    dw 60000
    db 5,6
    dw 3
query_tag: db 16
    db 23,0,160
    dw 60000
    db 1
query_end:
low_nibble: db 0

cursor: dl 0
query_setup:
 db 23,0,160
 dw 60000
 db 2
 db 23,0,160
 dw 60000
 db 0
 dw 4
 db 23,0,128,0
query_setup_end:
result_name: db "results.dat",0
file0: db "large.agnb",0
file1: db "again.agnb",0
file2: db "bad-id.agnb",0
file3: db "bad-raw.agnb",0
file4: db "late.agnb",0
file5: db "truncated.agnb",0

message: db 13,10,"AGNB plain-buffer loader run complete.",13,10
 db "Type dir at the MOS prompt and report to the agent that it works.",13,10
message_end:
 include "../../../api/agnb_dependencies.inc"
 include "../../../api/agnb_api.inc"
observations: blkb 128,0
