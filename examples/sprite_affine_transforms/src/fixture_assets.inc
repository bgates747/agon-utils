; One deliberately asymmetric 16x16 RGBA2222 fixture. It is used three ways:
; as a directly plotted bitmap, as a software sprite frame, and as a hardware
; sprite frame. RGBA2222 bytes are AA BB GG RR; zero is transparent.
;
; The corner markers are red/green/blue/white and the middle is a right arrow.
; A later asset pipeline may replace this table with INCBIN while retaining the
; public labels and exact width*height byte-count contract.

fixture_rgba2222_pixels:
    db 0c3h,0c3h,0c3h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0cch,0cch,0cch
    db 0c3h,0c3h,0c3h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0cch,0cch,0cch
    db 0c3h,0c3h,0c3h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0cch,0cch,0cch
    db 00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h
    db 00h,00h,00h,00h,00h,00h,00h,00h,00h,0cfh,00h,00h,00h,00h,00h,00h
    db 00h,00h,00h,00h,00h,00h,00h,00h,0cfh,0cfh,00h,00h,00h,00h,00h,00h
    db 00h,00h,00h,0f3h,0f3h,0f3h,0f3h,0f3h,0f3h,0f3h,0cfh,00h,00h,00h,00h,00h
    db 00h,00h,00h,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,00h,00h,00h,00h
    db 00h,00h,00h,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,0ffh,00h,00h,00h,00h
    db 00h,00h,00h,0f3h,0f3h,0f3h,0f3h,0f3h,0f3h,0f3h,0cfh,00h,00h,00h,00h,00h
    db 00h,00h,00h,00h,00h,00h,00h,00h,0cfh,0cfh,00h,00h,00h,00h,00h,00h
    db 00h,00h,00h,00h,00h,00h,00h,00h,00h,0cfh,00h,00h,00h,00h,00h,00h
    db 00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h
    db 0f0h,0f0h,0f0h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0ffh,0ffh,0ffh
    db 0f0h,0f0h,0f0h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0ffh,0ffh,0ffh
    db 0f0h,0f0h,0f0h,00h,00h,00h,00h,00h,00h,00h,00h,00h,00h,0ffh,0ffh,0ffh
fixture_rgba2222_pixels_end:

fixture_rgba2222_size: equ fixture_rgba2222_pixels_end-fixture_rgba2222_pixels
