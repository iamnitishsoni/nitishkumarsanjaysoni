import os
import yaml
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_rules():
    with open("data/tax_rules_fy25_26.yaml", "r") as file:
        return yaml.safe_load(file)


def calculate_with_llm(question):
    rules = load_rules()

    prompt = f"""
    You are an Indian income tax calculator.

    Use these tax rules:
    {rules}

    Calculate tax for this user:
    {question}

    Calculate both old and new tax regimes.

    Return only JSON in this format:
    {{
        "old_regime_tax": 0,
        "new_regime_tax": 0,
        "recommended_regime": "Old or New",
        "explanation": "Short explanation"
    }}

    Apply standard deduction, eligible deductions,
    rebate, surcharge, marginal relief and 4% cess.
    """

    chat = client.chats.create(
        model="gemini-3.5-flash-lite"
    )

    response = chat.send_message(prompt)
    result = response.text.strip()
    result = result.replace("```json", "").replace("```", "")

    return json.loads(result)


if __name__ == "__main__":
    question = """
    My annual salary is 1200000.
    My basic salary is 500000.
    I have 150000 in 80C.
    """

    result = calculate_with_llm(question)

    print(json.dumps(result, indent=4))
