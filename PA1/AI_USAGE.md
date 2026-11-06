# Project A — AI Usage Statement

## Tools used
- **ChatGPT:** Project planning, Python code drafting, debugging, test setup, benchmark interpretation and report preparation.
- **Google Gemini API:** Plain-language parsing, query-time tax calculation and conversion of YAML tax-rule data into JSON.

## How AI was used
AI assistance was used to draft and refine code for the parser, tax-engine integration, compiled-rules workflow and benchmarking. The code was run locally, errors were reviewed, and tests were executed.

Gemini was called by the application to interpret natural-language salary descriptions. The query-time calculator was benchmarked over 10 repeated calls and its results were not deterministic in that benchmark.

## Human review and validation
The Python rule engine was tested against 205 expected values supplied in the project dataset. The parser was tested against 50 natural-language examples and achieved 42/50 (84%). The compiled JSON rules were compared with YAML rules for one sample input under both regimes and matched.

These tests do not independently establish official tax-law correctness. Independent verification against at least 30 official calculator cases remains pending unless separate evidence is attached.

## Limitations
AI-generated code and rule conversions were reviewed through execution and testing, but should not be assumed correct merely because they run. The final tax calculation is performed by the Python rule engine rather than relying on Gemini's generated tax amount.
