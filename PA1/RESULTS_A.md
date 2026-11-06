# Project A — Results Report

## Project overview
This project compares three approaches to Indian salaried income-tax calculation: a Python rule engine, a Gemini query-time calculator, and a compiled-rules engine. A Gemini parser converts plain-language salary descriptions into structured input.

## Implementations
- **Rule engine:** Loads financial-year tax rules from YAML and calculates tax under old and new regimes.
- **Gemini query-time engine:** Uses Gemini to produce a tax result from a natural-language request.
- **Compiled-rules engine:** Loads JSON rules generated from YAML and uses the Python rule engine for calculations.
- **Parser:** Uses Gemini to extract salary and deduction fields from plain-language descriptions.

## Test results

| Component | Result | Interpretation |
|---|---:|---|
| Rule engine | 205/205 (100%) | Matches expected values in the supplied test dataset |
| Parser | 42/50 (84%) | Eight classifications differed from expected labels |
| Compiled engine | 2/2 (100%) | YAML and JSON results matched for one sample under both regimes |

**Important:** Passing the 205 supplied cases does not independently prove official tax-law accuracy. The compiled test is a limited consistency check, not broad validation.

## Performance benchmark
Ten runs per implementation:

| Metric | Rule engine | Compiled engine | Gemini |
|---|---:|---:|---:|
| Average latency | 0.0 s (rounded) | 0.0 s (rounded) | 1.89 s |
| Median latency | 0.0 s (rounded) | 0.0 s (rounded) | 1.7923 s |
| Fastest | 0.0 s (rounded) | 0.0 s (rounded) | 1.2222 s |
| Slowest | 0.0 s (rounded) | 0.0001 s | 2.5599 s |
| Deterministic | Yes | Yes | No |
| Runs | 10 | 10 | 10 |

Rule and compiled timings were displayed with limited precision. Re-measure with more decimal places before making fine-grained comparisons.

## Parser failure analysis
The parser scored 42/50 (84%). Eight mismatches were reported:
- Cases 6, 21, 23, 42 and 44: expected `ready`, got `needs_clarification`.
- Cases 36 and 39: expected `needs_clarification`, got `ready`.
- Case 46: expected `ready`, got `needs_clarification`.

Review the expected labels as well as the parser. A missing mediclaim amount or home-loan interest amount may reasonably require clarification. CTC is not necessarily the same as gross taxable salary.

## Findings
- The Python rule engine is the strongest choice for final tax arithmetic because it is deterministic in the benchmark.
- Gemini query-time calculation had higher latency and variable outputs across repeated calls.
- Compiled JSON rules matched YAML for the one sample tested; broader consistency tests are still needed.
- The parser can assist with language understanding but must validate fields and ask questions when important facts are missing.

## Pending validation and limitations
1. Verify at least 30 cases against the official income-tax calculator and retain inputs, outputs, dates and evidence.
2. Run YAML-versus-JSON consistency tests across the full test dataset.
3. Review the eight parser mismatches and correct parser logic or invalid expected labels.
4. Record Gemini token usage and calculate cost per 1,000 requests using applicable model pricing.
5. Re-measure rule and compiled latency with greater precision.
6. Validate FY 2025–26 rules against authoritative tax-law references.

Do not claim official verification, API cost measurement or complete legal correctness without supporting evidence.

## Conclusion
The current results support a hybrid design: use Gemini to interpret plain-language input, validate the extracted fields, and use deterministic Python rules for tax calculations. Annual rule updates should be reviewed and tested before use.

## 30-Case Audit — FY 2024-25

- Cases checked: 30
- Both-regime matches: 30/30
- Failures: 0
- Tolerance: ₹2
- Evidence: `results/official_30_audit.csv`
- Note: Compared against stored dataset reference values; independent official-calculator verification remains pending.
