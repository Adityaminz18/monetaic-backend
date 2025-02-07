import openai
import json
from typing import Dict, Any
from config import OPENAI_API_KEY, OPENAI_MODEL

# ✅ Set OpenAI API key
openai.api_key = OPENAI_API_KEY

async def call_openai(query: str) -> Dict[str, Any]:
    """
    Calls OpenAI API and returns a properly formatted JSON response.
    """
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial expert."},
                {"role": "user", "content": query}
            ],
            max_tokens=400
        )

        response_text = response["choices"][0]["message"]["content"].strip()
        if not response_text:
            raise ValueError("OpenAI API returned an empty response")

        return json.loads(response_text)  # ✅ Convert JSON response

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return {"error": "OpenAI API error. Please try again later."}
    except json.JSONDecodeError:
        print("JSON decoding error from OpenAI response.")
        return {"error": "Invalid JSON format from OpenAI"}
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return {"error": str(e)}

async def suggest_ideal_spending(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggests an ideal spending distribution based on best financial practices.
    """

    query = f"""
    You are a financial expert specializing in personal budgeting.
    Analyze the user's income and current spending patterns to suggest an **ideal spending breakdown**.

    **Financial Guidelines:**
    - **50% Essentials (Needs)** → Rent, food, utilities, transportation, insurance.
    - **30% Discretionary (Wants)** → Entertainment, dining out, shopping, non-essentials.
    - **20% Savings & Debt** → Savings, investments, debt payments, retirement funds.
    - **Adjustments**: If user has high debt, prioritize debt reduction in the savings portion.

    ### **User Data**
    {json.dumps(user_data, indent=2)}

    ### **Expected JSON Output Format**
    {{
        "income": {user_data.get("income", 0)},
        "ideal_allocation": {{
            "essentials": {{
                "percentage": 50,
                "recommended_budget": 0
            }},
            "discretionary": {{
                "percentage": 30,
                "recommended_budget": 0
            }},
            "savings_and_debt": {{
                "percentage": 20,
                "recommended_budget": 0
            }}
        }},
        "custom_recommendations": [
            "Recommendation 1",
            "Recommendation 2",
            "Recommendation 3"
        ]
    }}

    **Provide only JSON. No additional explanations.**
    """

    return await call_openai(query)
