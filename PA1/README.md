# Indian Salaried Income Tax Engine

## Project Overview
This project implements an Indian salaried income tax calculator using three approaches:

1. **Rule-Based Engine:** Python functions with YAML tax rules.
2. **LLM at Query Time:** Gemini API generates tax calculations from natural-language input.
3. **Compiled Rules Engine:** Loads YAML tax rules and calculates tax using Python functions.

## Project Structure

- `data/` – Tax rules and test datasets.
- `src/rule_engine.py` – Rule-based implementation.
- `src/llm_engine.py` – Gemini-based implementation.
- `src/compiled_engine.py` – YAML-based calculation implementation.
- `tests/test_all.py` – Automated test runner.
- `results/benchmark.txt` – Benchmark notes.

## Run the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run each implementation:

```bash
python src/rule_engine.py
python src/llm_engine.py
python src/compiled_engine.py
```

Run tests:

```bash
python tests/test_all.py
```

## Test Results

- Total supplied test cases: 205
- Passed: 205
- Failed: 0
- Reported accuracy against supplied expected outputs: 100%

## Limitations

- LLM calculations can vary between requests.
- API usage may involve latency and cost.
- The compiled engine currently loads YAML rules directly; automated Gemini rule compilation is not yet implemented.
- The test result reflects the supplied expected outputs and is not an independent verification of tax law.
- The three implementations have not yet been fully benchmarked against one another.
