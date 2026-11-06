import sys
import json
import os 

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, ".")

from rule_engine import load_rules, calculate_regime
from compiled_engine import load_compiled_rules

# Same sample input for both rule configurations
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

yaml_rules = load_rules("fy25_26")
compiled_rules = load_compiled_rules()

passed = 0
total = 2

for regime in ["old_regime", "new_regime"]:
    yaml_result = calculate_regime(person, regime, yaml_rules)
    compiled_result = calculate_regime(person, regime, compiled_rules)

    if yaml_result["tax"] == compiled_result["tax"]:
        passed += 1
        print(regime, "PASS")
    else:
        print(regime, "FAIL")
        print("YAML tax:", yaml_result["tax"])
        print("Compiled tax:", compiled_result["tax"])

print("Passed:", passed, "/", total)
