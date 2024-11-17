    MACRO LOAD_FLOAT ARG
    ld ix,$+9
    call VAL_FP
    asciz ARG
    ENDMACRO

    DB 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37

    LOAD_FLOAT "1.234567"

VAL_FP:
    ret