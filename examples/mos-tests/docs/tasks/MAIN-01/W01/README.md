# MAIN-01 W01 — Historical inventory evidence

**Historical evidence only. Do not use archived API text as current guidance.**
Start with the maintained [MOS API inventory](../../../mos-api-inventory.md),
identify the actual target version, and consult the pinned upstream contracts.

1. `api-register.json` is a compact index of selectors, source labels and line
   references. It contains no copied API descriptions.
2. `identity.json` records the original baseline and hashes. Its `references/*`
   paths name members of `historical-reference.tar.gz`, not live project files.
3. `historical-reference.tar.gz` contains the original snapshots, full extracted
   register and original inventory. It is retained for provenance, not routine
   research. Ordinary project searches should use the maintained index.
4. `historical-reference.sha256` fingerprints the archive. Every archived input
   was verified byte-for-byte before removing its loose duplicate.
5. No API test or firmware repair was performed during this documentation change.
