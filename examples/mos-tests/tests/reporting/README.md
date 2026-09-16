# Decoder/report qualification

Run human/mos-tests report-check --output FRESH_DIRECTORY on Linux. check.py
constructs literal wire/manifest fixtures without importing production serializers,
then exercises scripts/report_results.py and its CLI. The 14 report expectations
come from the frozen fixtures/format-v1/report-oracles.json. Binary frozen vectors
are read, never regenerated. Each run retains input manifests, binary evidence,
expected readable examples, CLI reports and result.json. All data are synthetic;
placeholder target identities are deliberately declared as such. These tests
qualify parsing/report semantics, not hardware or actual MOS conformance.
