import yaml


def load_rules(year="fy25_26"):
    filename = "data/tax_rules_" + year + ".yaml"

    with open(filename, "r") as file:
        return yaml.safe_load(file)


def calculate_tax(income, slabs):
    tax = 0

    for slab in slabs:
        lower = slab["min"]
        upper = slab["up_to"]
        rate = slab["rate"]

        if upper is None:
            taxable = income - lower
        else:
            taxable = min(income, upper) - lower

        if taxable > 0:
            tax = tax + taxable * rate

    return tax


def calculate_hra(data):
    salary = data["basic_salary"] + data.get("da", 0)

    if salary == 0:
        return 0

    rent = data.get("rent_paid", 0)
    hra = data.get("hra_received", 0)

    if data.get("is_metro", False):
        percentage = 0.50
    else:
        percentage = 0.40

    amount1 = hra
    amount2 = rent - (salary * 0.10)
    amount3 = salary * percentage

    return max(0, min(amount1, amount2, amount3))


def apply_surcharge(tax, income, regime, rules):
    thresholds = rules["common"]["surcharge_thresholds"][regime]

    surcharge_rate = 0
    threshold_value = 0

    for item in thresholds:
        if income > item["threshold"]:
            surcharge_rate = item["rate"]
            threshold_value = item["threshold"]

    if surcharge_rate == 0:
        return tax

    surcharge = tax * surcharge_rate

    # Marginal relief at surcharge threshold
    if threshold_value > 0:
        tax_at_threshold = calculate_tax(
            threshold_value,
            rules[regime]["slabs"]
        )

        maximum_tax = tax_at_threshold + (income - threshold_value)

        if tax + surcharge > maximum_tax:
            surcharge = max(0, maximum_tax - tax)

    return tax + surcharge


def calculate_regime(data, regime, rules):
    details = rules[regime]

    income = data["gross_salary"]
    income = income - details["standard_deduction"]

    if regime == "old_regime":
        income = income - calculate_hra(data)

        deductions = details["deductions_allowed"]

        income = income - min(data.get("sec_80c", 0),
                              deductions["section_80c_max"])

        income = income - min(data.get("sec_80ccd_1b", 0),
                              deductions["section_80ccd_1b_max"])

        d80 = deductions["section_80d"]

        if data.get("is_self_senior", False):
            self_limit = d80["self_family_senior_max"]
        else:
            self_limit = d80["self_family_max"]

        if data.get("are_parents_senior", False):
            parent_limit = d80["parents_senior_max"]
        else:
            parent_limit = d80["parents_max"]

        income = income - min(data.get("sec_80d_self", 0), self_limit)
        income = income - min(data.get("sec_80d_parents", 0), parent_limit)

        income = income - min(
            data.get("home_loan_interest", 0),
            deductions["home_loan_interest_max"]
        )

    income = max(0, income)

    tax = calculate_tax(income, details["slabs"])

    rebate = details["section_87a"]

    if income <= rebate["max_taxable_income"]:
        tax = max(0, tax - rebate["max_rebate_amount"])

    elif rebate["marginal_relief_applicable"]:
        extra_income = income - rebate["max_taxable_income"]
        tax = min(tax, extra_income)

    tax = apply_surcharge(tax, income, regime, rules)

    tax = tax + (tax * rules["common"]["cess_rate"])

    # Round tax to nearest 10 rupees
    tax = round(tax / 10) * 10

    return {
        "taxable_income": income,
        "tax": round(tax, 2)
    }


if __name__ == "__main__":
    rules = load_rules()

    person = {
        "gross_salary": 1200000,
        "basic_salary": 500000,
        "da": 0,
        "hra_received": 200000,
        "rent_paid": 180000,
        "is_metro": True,
        "sec_80c": 150000,
        "sec_80ccd_1b": 50000,
        "sec_80d_self": 25000,
        "is_self_senior": False,
        "sec_80d_parents": 0,
        "are_parents_senior": False,
        "home_loan_interest": 0
    }

    old_tax = calculate_regime(person, "old_regime", rules)
    new_tax = calculate_regime(person, "new_regime", rules)

    print("Old Regime:", old_tax)
    print("New Regime:", new_tax)

    if old_tax["tax"] < new_tax["tax"]:
        print("Better option: Old Regime")
    elif new_tax["tax"] < old_tax["tax"]:
        print("Better option: New Regime")
    else:
        print("Both regimes have equal tax")
