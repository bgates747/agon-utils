# W05 interpreter selection

The Author selected Jeroen Venema (envenomator)'s BBC BASIC V in eZ80 ADL mode
as the first interpreter. The Linux reference checkout already exists, so no
clone or upstream change was required.

1. Checkout: `/home/smith/Agon/bbc-basic-v-adl`.
2. Origin: https://github.com/envenomator/agon-bbc-basic.git
3. Inspected clean source HEAD: `861085c472edbbb89080c3bd9cfd6a2a47360a62`,
   tag `v1.0RC1`, dated 2026-07-05. This records the installed checkout, not a
   claim that it is the newest upstream revision.
4. Existing generated binary: `bin/basic.bin`, 25499 bytes;
   SHA256 `ed6ff5a4707f941ff7b178111771a0bfade3ecdefccbb3bcb4015b9a6d5a87ab`. Its build provenance has not yet been independently
   reproduced, and it must not be labeled a downloaded release asset.
5. Tom's curated SD-card repository is `tomm/popup-mos`. The installed Fab 1.2.4
   submodule has `bbcbasic.bin` and `bbcbasic24.bin`, identified by its README
   as breakintoprogram's Z80 and ADL ports; neither identifies Jeroen's V port.
   Filenames or the word ADL alone are insufficient interpreter provenance.
6. Read the selected checkout README and `docs/agonplatform.md`. This port
   supports plain-text `.BAS`, `.TXT`, `.ASC`; `.BBC` is tokenized BBC BASIC Z80
   format and the default extension. Inline assembler defaults to ADL 1.
   `*VERSION` reports this port's Agon release; `*BYE`/QUIT exits to MOS.
7. W05 fixtures should explicitly identify this interpreter/port, version/hash,
   source format, and mode. Legacy BASIC compatibility must be established per
   fixture rather than inferred from sparse legacy documentation.

W05 is complete: provenance was confirmed by a byte-identical rebuild and
raw-image execution passed. See README.md for deployment and result evidence.

## Deployment naming

The Author specifies `bbc-basic-v-adl.bin` as this interpreter's project and
SD-image deployment filename. Copy the identified upstream `bin/basic.bin`
under that name and verify identical bytes/hashes. Keep the upstream checkout
unchanged. Fixtures and launch commands must use `bbc-basic-v-adl.bin`; record
upstream `basic.bin` only as the source artifact name in provenance.
