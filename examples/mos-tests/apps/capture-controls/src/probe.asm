.assume adl=1
.section .text
.global _run_capture_controls
.global _sample_done
.global _controls_done
_run_capture_controls:
 push ix
 push iy
 ld (_saved_sp), sp
 ld hl, 0b7e000h
 ld de, 0b7e001h
 ld bc, 01fffh
 ld (hl), 0c7h
 ldir
 in0 a, (0b5h)
 ld (_ram_upper), a
 in0 a, (0b4h)
 ld (_ram_ctl), a
 ld hl, 0
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 1
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld bc, 010283h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 2
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld bc, 018203h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 3
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld bc, 810203h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 4
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld de, 040586h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 5
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld de, 048506h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 6
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld de, 840506h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 7
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 070889h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 8
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 078809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 9
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 870809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 10
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld ix, 0a0b8ch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 11
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld ix, 0a8b0ch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 12
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld ix, 8a0b0ch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 13
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld iy, 0d0e8fh
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 14
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld iy, 0d8e0fh
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 15
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld iy, 8d0e0fh
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 16
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld a, 0dah
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 17
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005aa4h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 18
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005aa7h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 19
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005aa1h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 20
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005aadh
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 21
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005ab5h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 22
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005a85h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 23
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005ae5h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 24
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 ld hl, 005a25h
 push hl
 pop af
 ld hl, 070809h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 25
 ld (_sample_index), hl
 ld hl, 005aa5h
 push hl
 pop af
 ld bc, 010203h
 ld de, 040506h
 ld hl, 070809h
 ld ix, 0a0b0ch
 ld iy, 0d0e0fh
 call _capture_before
 inc sp
 inc sp
 inc sp
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 26
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 27
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld bc, 0fefd7ch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 28
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld bc, 0fe7dfch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 29
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld bc, 7efdfch
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 30
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld de, 0fbfa79h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 31
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld de, 0fb7af9h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 32
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld de, 7bfaf9h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 33
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 0f8f776h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 34
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 0f877f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 35
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 78f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 36
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld ix, 0f5f473h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 37
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld ix, 0f574f3h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 38
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld ix, 75f4f3h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 39
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld iy, 0f2f170h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 40
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld iy, 0f271f0h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 41
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld iy, 72f1f0h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 42
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld a, 25h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 43
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a55bh
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 44
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a558h
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 45
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a55eh
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 46
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a552h
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 47
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a54ah
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 48
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a57ah
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 49
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a51ah
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 50
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 ld hl, 00a5dah
 push hl
 pop af
 ld hl, 0f8f7f6h
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
 ld hl, 51
 ld (_sample_index), hl
 ld hl, 00a55ah
 push hl
 pop af
 ld bc, 0fefdfch
 ld de, 0fbfaf9h
 ld hl, 0f8f7f6h
 ld ix, 0f5f4f3h
 ld iy, 0f2f1f0h
 call _capture_before
 inc sp
 inc sp
 inc sp
 call _capture_after
 ld sp, (_saved_sp)
 call _clobber_after_capture
 call _sample_done
_controls_done:
 pop iy
 pop ix
 ret
_sample_done:
 ret
_clobber_after_capture:
 ld hl, 0
 ld bc, 0
 ld de, 0
 ld ix, 0
 ld iy, 0
 xor a
 ret
.section .data
.global _sample_index
_sample_index: db 0,0,0
.global _ram_upper
_ram_upper: db 0
_ram_ctl: db 0
_saved_sp: db 0,0,0
.include "../runner/src/capture.asm"
