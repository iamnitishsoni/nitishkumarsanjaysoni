import os
import yaml
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def compile_rules():
    with open("data/tax_rules_fy25_26.yaml", "r") as file:
        tax_rules = file.read()

    prompt = f"""
    Convert the following Indian income tax rules into JSON.

    Preserve every rule, threshold, slab, deduction, rebate,
    surcharge and cess rate exactly.

    Do not calculate tax.
    Do not change any numbers.
    Do not remove any fields.

    Return only valid JSON with the same structure as the YAML.

    TAX RULES:
    {tax_rules}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()
    result = result.replace("```json", "").replace("```", "")

    compiled_rules = json.loads(result)

    with open("data/compiled_rules.json", "w") as file:
        json.dump(compiled_rules, file, indent=4)

    print("Rules compiled successfully.")
    print("Saved to data/compiled_rules.json")


if __name__ == "__main__":
    compile_rules()
