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

    .platform 0x4000 :
    {
        KEEP(*(.platform))
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
    ASSERT(__io_trap == 0x4000, "I/O trap moved")
    ASSERT(__platform_end <= 0x5000, "platform adapter overlaps reference ROM")
    ASSERT(__original_rom == 0x5000, "reference ROM moved")
    ASSERT(__original_rom_end - __original_rom == 0x2000, "reference ROM is not 8 KiB")
    ASSERT(__start == 0x8000, "proof loader moved into original address space")
    ASSERT(__image_end <= 0x10000, "adapter proof exceeds one 64 KiB bank")
}
