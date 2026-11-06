import sys
sys.path.insert(0, ".")
import json
from src.rule_engine import load_rules, calculate_regime

with open("data/test_cases_200.json", "r") as file:
    test_cases = json.load(file)

rules = load_rules("fy24_25")

passed = 0
failed = 0

for test in test_cases:
    person = test["input"]

    old_result = calculate_regime(person, "old_regime", rules)
    new_result = calculate_regime(person, "new_regime", rules)

    expected_old = test["expected_old_regime_tax"]
    expected_new = test["expected_new_regime_tax"]

    old_match = abs(old_result["tax"] - expected_old) <= 2
    new_match = abs(new_result["tax"] - expected_new) <= 2

    if old_match and new_match:
        passed += 1
    else:
        failed += 1

        if failed <= 10:
            print("\nFailed test:", test["test_id"])
            print("Expected old:", expected_old)
            print("Actual old:", old_result["tax"])
            print("Expected new:", expected_new)
            print("Actual new:", new_result["tax"])

print("\nTEST RESULTS")
print("Total tests:", len(test_cases))
print("Passed:", passed)
print("Failed:", failed)
print("Accuracy:", round(passed / len(test_cases) * 100, 2), "%")


