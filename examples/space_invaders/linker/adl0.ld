ENTRY(__start)

MEMORY
{
    Z80RAM (rwx) : ORIGIN = 0x0000, LENGTH = 0x10000
}

SECTIONS
{
    . = ORIGIN(Z80RAM);

    .init :
    {
        KEEP(*(.init))
    } > Z80RAM

    .text :
    {
        *(.text .text.*)
    } > Z80RAM

    .rodata :
    {
        *(.rodata .rodata.*)
    } > Z80RAM

    .data :
    {
        *(.data .data.*)
    } > Z80RAM

    .bss (NOLOAD) :
    {
        *(.bss .bss.* COMMON)
    } > Z80RAM

    /DISCARD/ :
    {
        *(.comment)
    }

    ASSERT(__image_start == 0x0000, "ADL=0 image must begin at logical address 0")
    ASSERT(__mos_header == 0x0040, "MOS header must be at file offset 0x40")
    ASSERT(__start == 0x0045, "ADL=0 entry must immediately follow the MOS header")
    ASSERT(__image_end <= 0x10000, "ADL=0 image exceeds one 64 KiB bank")
}
