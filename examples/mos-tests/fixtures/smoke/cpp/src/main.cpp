#include <agon/mos.h>
int main() {
    const char message[] = "W04: MOS ABI 0123456789 AaZz !?\r\n";
    for (const char* p = message; *p; ++p) {
        putch(static_cast<unsigned char>(*p));
    }
    // Deliberate 24-bit result: debugger stops before crt0 propagates it to MOS.
    return 0x123456;
}
