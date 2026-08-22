; Direct-GPIO architecture probe for the Space Invaders port.
;
; Bundles Tom's stock-MOS static GPIO video driver, installs it at 0x0b8000,
; selects mode 8 (320x240 RGB332, 15 kHz, 60 Hz), points scanout at 0x080000,
; and draws an orientation test around a centered 256x224 raster aperture.

	.assume adl=0
	.section .init, "ax", @progbits
	.global __image_start
	.global __mos_header
	.global __start
	.global __image_end

	.equ VIDAPI_GETVERSION, 0
	.equ VIDAPI_SETMODE, 1
	.equ VIDAPI_GETVIDEOSETUP, 2
	.equ VIDAPI_VIDEOSTOP, 4
	.equ VIDAPI_POLLKEYBOARDEVENT, 8

	.equ MOSLET_LOAD_BASE, 0x040000
	.equ GPIO_DRIVER_ENTRY, 0x0b8000
	.equ GPIO_MODE_320X240_60HZ, 8
	.equ FRAMEBUFFER, 0x080000
	.equ FRAMEBUFFER_SIZE, 320 * 240
	.equ APERTURE_X, 32
	.equ APERTURE_Y, 8
	.equ APERTURE_WIDTH, 256
	.equ APERTURE_HEIGHT, 224

__image_start:
	jp __start
	.byte 0
	.space 0x3c, 0

__mos_header:
	.ascii "MOS"
	.byte 0
	.byte 0

__start:
	ld sp, 0xfffe
	push.lil ix
	push.lil iy

	call load_gpio_video_driver

	ld a, VIDAPI_GETVERSION
	call.lil GPIO_DRIVER_ENTRY
	or a
	jr z, no_driver

	call clear_framebuffer
	call draw_orientation_pattern

	ld a, VIDAPI_GETVIDEOSETUP
	call.lil GPIO_DRIVER_ENTRY
	ld a, FRAMEBUFFER & 0xff
	ld.lil (iy+1), a
	ld a, (FRAMEBUFFER >> 8) & 0xff
	ld.lil (iy+2), a
	ld a, (FRAMEBUFFER >> 16) & 0xff
	ld.lil (iy+3), a

	ld a, VIDAPI_SETMODE
	ld l, GPIO_MODE_320X240_60HZ
	call.lil GPIO_DRIVER_ENTRY

wait_for_key:
	ld a, VIDAPI_POLLKEYBOARDEVENT
	ld de, key_event
	call.lil GPIO_DRIVER_ENTRY
	or a
	jr z, wait_for_key
	ld a, (key_is_down)
	or a
	jr z, wait_for_key

	ld a, VIDAPI_VIDEOSTOP
	call.lil GPIO_DRIVER_ENTRY
	jr exit_success

no_driver:
	ld hl, no_driver_message
	ld bc, 0
	xor a
	rst.lis 0x18

exit_success:
	pop.lil iy
	pop.lil ix
	ld hl, 0
	ret.lis

; Stock MOS does not expose Rainbow MOS's reset-vector API. Copy Tom's
; position-fixed static driver into high MOSlet RAM and call it directly.
load_gpio_video_driver:
	di
	ld.lil hl, MOSLET_LOAD_BASE + gpio_video_driver_image
	ld.lil de, GPIO_DRIVER_ENTRY
	ld.lil bc, gpio_video_driver_image_end - gpio_video_driver_image
	ldir.lil
	ei
	ret

; Clear the complete 320x240 RGB332 framebuffer at an absolute 24-bit address.
clear_framebuffer:
	ld.lil hl, FRAMEBUFFER
	ld.lil de, FRAMEBUFFER + 1
	ld.lil bc, FRAMEBUFFER_SIZE - 1
	xor a
	ld.lil (hl), a
	ldir.lil
	ret

; Draw a 256x224 box centered at (32,8). The differently coloured edges and
; white centre cross make rotation, reflection, clipping, and centring visible.
draw_orientation_pattern:
	; Top edge: red.
	ld.lil hl, FRAMEBUFFER + APERTURE_Y * 320 + APERTURE_X
	ld a, 0xe0
	call draw_256_pixels

	; Bottom edge: blue.
	ld.lil hl, FRAMEBUFFER + (APERTURE_Y + APERTURE_HEIGHT - 1) * 320 + APERTURE_X
	ld a, 0x03
	call draw_256_pixels

	; Horizontal centre: white.
	ld.lil hl, FRAMEBUFFER + (APERTURE_Y + APERTURE_HEIGHT / 2) * 320 + APERTURE_X
	ld a, 0xff
	call draw_256_pixels

	; Left edge: green.
	ld.lil hl, FRAMEBUFFER + APERTURE_Y * 320 + APERTURE_X
	ld a, 0x1c
	call draw_224_rows

	; Right edge: magenta.
	ld.lil hl, FRAMEBUFFER + APERTURE_Y * 320 + APERTURE_X + APERTURE_WIDTH - 1
	ld a, 0xe3
	call draw_224_rows

	; Vertical centre: white.
	ld.lil hl, FRAMEBUFFER + APERTURE_Y * 320 + APERTURE_X + APERTURE_WIDTH / 2
	ld a, 0xff
	call draw_224_rows
	ret

draw_256_pixels:
	ld b, 0
1:
	ld.lil (hl), a
	inc.lil hl
	djnz 1b
	ret

draw_224_rows:
	ld c, APERTURE_HEIGHT
	ld.lil de, 320
1:
	ld.lil (hl), a
	add.lil hl, de
	dec c
	jr nz, 1b
	ret

key_event:
key_ascii:
	.byte 0
key_modifiers:
	.byte 0
key_vkey:
	.byte 0
key_is_down:
	.byte 0

no_driver_message:
	.asciz "Static GPIO video driver failed\r\n"

	.balign 4
gpio_video_driver_image:
	.incbin "third_party/ez80-framebuffer-agon/gpiovideodriver_static_0xb8000.lib"
gpio_video_driver_image_end:

__image_end:
