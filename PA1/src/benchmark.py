import sys
sys.path.insert(0, ".")

import time
import json
import statistics

from rule_engine import load_rules, calculate_regime
from compiled_engine import calculate_compiled_tax
from llm_engine import calculate_with_llm


person = {
    "gross_salary": 1200000,
    "basic_salary": 500000,
    "da": 0,
    "hra_received": 0,
    "rent_paid": 0,
    "is_metro": False,
    "sec_80c": 150000,
    "sec_80ccd_1b": 0,
    "sec_80d_self": 0,
    "is_self_senior": False,
    "sec_80d_parents": 0,
    "are_parents_senior": False,
    "home_loan_interest": 0
}

question = """
My annual gross salary is 12 lakh.
My basic salary is 5 lakh.
I have invested 1.5 lakh under 80C.
"""


def measure_rule_engine():
    rules = load_rules("fy25_26")
    times = []
    results = []

    for i in range(10):
        start = time.time()

        old_result = calculate_regime(person, "old_regime", rules)
        new_result = calculate_regime(person, "new_regime", rules)

        times.append(time.time() - start)

        results.append({
            "old": old_result["tax"],
            "new": new_result["tax"]
        })

    return times, results


def measure_compiled_engine():
    times = []
    results = []

    for i in range(10):
        start = time.time()
        result = calculate_compiled_tax(person)
        times.append(time.time() - start)
        results.append(result)

    return times, results


def measure_llm():
    times = []
    results = []

    for i in range(10):
        start = time.time()
        result = calculate_with_llm(question)
        times.append(time.time() - start)
        results.append(result)

    return times, results


def show_result(name, times, results):
    print("\n", name)
    print("Runs:", len(times))
    print("Average latency:", round(statistics.mean(times), 4), "seconds")
    print("Median latency:", round(statistics.median(times), 4), "seconds")
    print("Fastest:", round(min(times), 4), "seconds")
    print("Slowest:", round(max(times), 4), "seconds")
    print("Deterministic:", all(x == results[0] for x in results))


if __name__ == "__main__":
    times, results = measure_rule_engine()
    show_result("RULE ENGINE", times, results)

    times, results = measure_compiled_engine()
    show_result("COMPILED ENGINE", times, results)

    print("\nRunning Gemini 10 times. This will use API requests.")
    times, results = measure_llm()
    show_result("GEMINI ENGINE", times, results)
