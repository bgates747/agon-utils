#pragma once
// Check before using the fixed SRAM window. This call changes registers.
extern "C" int capture_available();
// Assembly-only observation entry points: do not use C++ calls to observe raw
// caller registers, because its ABI/prologue changes the observation boundary.
// _capture_before writes 32 bytes at B7E900; _capture_after at B7E920.
// Both preserve primary registers/flags and return with balanced caller SP.
// Require ADL=1, MB=0, a valid writable stack (six bytes headroom: call + push),
// verified SRAM mapping, and no nested capture or concurrent user writer.
