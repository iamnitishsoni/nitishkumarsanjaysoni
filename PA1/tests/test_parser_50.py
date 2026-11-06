import sys
import time
sys.path.insert(0, ".")

import json

from src.parser import parse_input


with open("data/plain_language_50.json", "r") as file:
    examples = json.load(file)

passed = 0
failed = 0

for example in examples:
    result = parse_input(example["text"])

    expected = example["expected_status"]
    actual = result["status"]

    if expected == actual:
        passed += 1
    else:
        failed += 1
        print("\nFailed:", example["id"])
        print("Text:", example["text"])
        print("Expected:", expected)
        print("Actual:", actual)

    print("Waiting 5 second for next call!")
    time.sleep(5)
print("\nPARSER RESULTS")
print("Total:", len(examples))
print("Passed:", passed)
print("Failed:", failed)
print("Accuracy:", round(passed / len(examples) * 100, 2), "%")
