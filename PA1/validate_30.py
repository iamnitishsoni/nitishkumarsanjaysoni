import json
import csv
import os
import sys

# Run this from the PA1 project root:
# python validate_30.py

sys.path.insert(0, os.path.abspath("src"))
from rule_engine import load_rules, calculate_regime

DATA_FILE = "data/test_cases_200.json"
OUTPUT_FILE = "results/official_30_audit.csv"
TOLERANCE = 2  # rupees

with open(DATA_FILE, "r", encoding="utf-8") as f:
    cases = json.load(f)

selected = [
    case for case in cases
    if case.get("category") == "official_verified_30"
][:30]

if len(selected) != 30:
    raise SystemExit(f"Expected 30 tagged cases, found {len(selected)}")

rules = load_rules("fy24_25")
os.makedirs("results", exist_ok=True)

rows = []
passed = 0

for case in selected:
    person = case["input"]

    old_actual = calculate_regime(person, "old_regime", rules)["tax"]
    new_actual = calculate_regime(person, "new_regime", rules)["tax"]

    old_expected = case["expected_old_regime_tax"]
    new_expected = case["expected_new_regime_tax"]

    old_match = abs(old_actual - old_expected) <= TOLERANCE
    new_match = abs(new_actual - new_expected) <= TOLERANCE
    status = "PASS" if old_match and new_match else "FAIL"

    if status == "PASS":
        passed += 1

    rows.append({
        "test_id": case["test_id"],
        "description": case.get("description", ""),
        "dataset_claims_official_verified": case.get("verified_official_calculator", False),
        "old_expected": old_expected,
        "old_calculated": old_actual,
        "old_match": old_match,
        "new_expected": new_expected,
        "new_calculated": new_actual,
        "new_match": new_match,
        "overall_status": status
    })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n30-CASE LOCAL AUDIT")
print("Financial year: FY 2024-25 (AY 2025-26)")
print(f"Cases checked: {len(rows)}")
print(f"Both-regime matches: {passed}/30")
print(f"Failures: {30 - passed}/30")
print(f"CSV saved to: {OUTPUT_FILE}")
print("\nNOTE: This script compares the Python engine with expected values stored")
print("in your dataset. It does NOT independently access or verify the official")
print("Income Tax Department calculator. Retain official calculator evidence")
print("for any case you claim was independently checked.")
