# Project A — Architecture Decision Matrix

## Decision
Use a hybrid architecture: Gemini for natural-language parsing, followed by validation and a deterministic Python rule engine for tax calculations.

## Comparison

| Criterion | Python rule engine | Gemini at query time | Compiled JSON rules |
|---|---|---|---|
| Determinism | Yes in current benchmark | No in current benchmark | Yes in current benchmark |
| Latency | Very low; display rounded | Average 1.89 seconds | Very low; display rounded |
| Natural-language input | Needs structured input | Supports natural language | Needs structured input |
| Auditability | High with versioned rules/code | Lower; output can vary | High if source and compiled rules are compared |
| Current tests | 205 supplied cases passed | 10-run latency/determinism test | One sample, both regimes, matched YAML |

## Proposed flow
1. User enters a plain-language salary description.
2. Gemini extracts structured fields.
3. The application validates fields and asks clarification questions when needed.
4. Validated data is passed to the Python rule engine.
5. The engine calculates old- and new-regime tax using versioned rules.
6. The application returns both results, the lower-tax recommendation and an explanation.

## Rationale
The rule engine passed 205 supplied expected-value tests and was deterministic across 10 benchmark runs. Gemini was non-deterministic across 10 runs and had an average latency of 1.89 seconds. Therefore, Gemini should interpret language, not act as the authoritative tax calculator.

## Risks and controls

| Risk | Control |
|---|---|
| Parser misunderstands salary/deductions | Validate fields and ask clarification questions |
| CTC mistaken for taxable gross salary | Treat CTC as ambiguous until its components are known |
| Model invents missing amounts | Prohibit guessing and validate required fields |
| Tax rules become outdated | Version rules by financial year and review annual changes |
| YAML-to-JSON conversion changes values | Compare all keys/values and run full consistency tests |
| Incorrect tax output | Maintain independent tests and official-calculator evidence |

## Final decision
Use the hybrid design. Do not rely on Gemini's generated tax amount as the authoritative result.
