# Local acceptance evidence

Measured on 2026-10-01, Windows, Python 3.12.10, CPU only.

- pytest: 34 passed.
- Installed spc executable: three separate processes for fixtures, run and markdown report completed in 0.757 seconds, below the five-second threshold.
- Synthetic records: 200; explicit sections present: 50; needs clarification: 150; missing requirements: 100; missing acceptance: 100.
- Every issue ID matched independent hand-computed expectations exactly. Planted rule detection: zero false positives and zero missed cases on these synthetic fixtures.
- Repeated report bytes match. A changed description changes computed counts. Corrupt cached counts are recomputed.
- No real trial data or measured savings were available. Benchmark duration measures local execution only, not time saved or future performance.

The verdict remains pending the two-week real-use window. See VERDICT.md and README.md.
