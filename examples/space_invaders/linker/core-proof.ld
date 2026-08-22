ENTRY(__start)

MEMORY
{
    Z80RAM (rwx) : ORIGIN = 0x0000, LENGTH = 0x10000
}

SECTIONS
{
    . = ORIGIN(Z80RAM);

    .boot :
    {
        KEEP(*(.boot))
    } > Z80RAM

    .core_test 0x4000 :
    {
        KEEP(*(.core_test))
    } > Z80RAM

    .original_rom 0x5000 :
    {
        KEEP(*(.original_rom))
    } > Z80RAM

    .loader 0x8000 :
    {
        KEEP(*(.loader))
    } > Z80RAM

    /DISCARD/ :
    {
        *(.comment)
    }

    ASSERT(__image_start == 0x0000, "ADL=0 image must begin at logical address 0")
    ASSERT(__mos_header == 0x0040, "MOS header must be at file offset 0x40")
    ASSERT(__start == 0x8000, "proof loader moved into original address space")
    ASSERT(__core_test_start == 0x4000, "core-test trampoline moved")
    ASSERT(__core_test_end <= 0x5000, "core-test trampoline overlaps reference ROM")
    ASSERT(__original_rom == 0x5000, "reference ROM moved")
    ASSERT(__original_rom_end - __original_rom == 0x2000, "reference ROM is not 8 KiB")
    ASSERT(__image_end <= 0x10000, "core proof exceeds one 64 KiB bank")
}
