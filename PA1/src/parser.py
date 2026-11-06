import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def parse_input(question):
    prompt = f"""
    Convert this Indian salaried person's description into JSON.

    User description:
    {question}

    Return only valid JSON with these fields:

    {{
        "status": "ready or needs_clarification",
        "gross_salary": null,
        "basic_salary": null,
        "da": 0,
        "hra_received": null,
        "rent_paid": null,
        "is_metro": null,
        "sec_80c": 0,
        "sec_80ccd_1b": 0,
        "sec_80d_self": 0,
        "is_self_senior": false,
        "sec_80d_parents": 0,
        "are_parents_senior": null,
        "home_loan_interest": 0,
        "missing_fields": [],
        "question": ""
    }}

    Rules:
    - Convert LPA and Lakhs into rupees.
    - Convert monthly rent into annual rent.
    - Understand Hinglish.
    - Never invent missing amounts.
    - If salary is missing, ask for gross salary.
    - If rent or HRA is mentioned but rent is unclear, ask for rent.
    - If HRA is mentioned but basic salary is missing, ask for basic salary.
    - If rent is mentioned but city is unclear, ask whether it is metro.
    - If parents' insurance is mentioned but their age category is unclear,
      ask whether they are senior citizens.
    - If important information is missing, use needs_clarification.
    - If the description contradicts itself, ask for clarification.
    - Ignore deductions not allowed under the new regime when calculating
      that regime, but preserve the user's input.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()
    result = result.replace("```json", "").replace("```", "")

    return json.loads(result)


if __name__ == "__main__":
    question = input("Describe your salary and deductions: ")

    result = parse_input(question)

    print(json.dumps(result, indent=4))
