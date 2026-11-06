import sys
sys.path.insert(0, ".")

import json

from rule_engine import calculate_regime


def load_compiled_rules():
    with open("data/compiled_rules.json", "r") as file:
        return json.load(file)


def calculate_compiled_tax(person):
    rules = load_compiled_rules()

    old_result = calculate_regime(person, "old_regime", rules)
    new_result = calculate_regime(person, "new_regime", rules)

    if old_result["tax"] < new_result["tax"]:
        recommended = "Old"
    elif new_result["tax"] < old_result["tax"]:
        recommended = "New"
    else:
        recommended = "Either"

    return {
        "old_regime_tax": old_result["tax"],
        "new_regime_tax": new_result["tax"],
        "recommended_regime": recommended
    }


if __name__ == "__main__":
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

    result = calculate_compiled_tax(person)
    print(json.dumps(result, indent=4))
