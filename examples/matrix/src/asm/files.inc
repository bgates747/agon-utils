filedata: equ 0xB7E000 ; address of onboard 8k sram

f16_fil: equ $
f16_filinfo: equ f16_fil + fil_struct_size

f16_fil_out: equ f16_filinfo + filinfo_struct_size
f16_filinfo_out: equ f16_fil_out + fil_struct_size