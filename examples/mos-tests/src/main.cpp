#include <agon/mos.h>

// Exercise the installed C++ -> libagon -> MOS character-output path.
// This marker reports reaching main; visual correctness is checked by the operator.
int main() {
    const char message[] = "MOS-TESTS W03: C++ -> MOS output reached\r\n";
    for (const char* cursor = message; *cursor; ++cursor) {
        putch(static_cast<unsigned char>(*cursor));
    }
    return 0;
}
