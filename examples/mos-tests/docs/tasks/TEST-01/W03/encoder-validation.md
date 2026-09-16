# TEST-01 W03 — encoder portion

Encoder checks completed alongside MAIN-03 W04: six frozen record types and the
control slot match, payload/UTF-8/buffer boundaries are checked, and the independent
qualification parser rejects 684 truncated prefixes plus 690 single-bit mutations.
See [evidence](../../MAIN-03/W04/validation.md). W03 remains open: the production
decoder, manifest identities, sequence/order/conflict handling and labelled
recovery interpretation are W05 work. Do not count this partial check as closure.
