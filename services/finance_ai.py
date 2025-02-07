import openai
import json
import re
from typing import Dict, Any, List
from bson import ObjectId
from config import OPENAI_API_KEY, OPENAI_MODEL

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def convert_objectid(obj):
    """Convert MongoDB ObjectId to string recursively in dictionaries/lists."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    return obj

def extract_json(response_text: str) -> Dict[str, Any]:
    """
    Extracts only the JSON part from OpenAI's response.
    Handles cases where OpenAI returns text before/after the JSON.
    """
    try:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)  # Extracts first JSON block
        if match:
            return json.loads(match.group(0))  # Return parsed JSON
        else:
            raise ValueError("No JSON found in OpenAI response")
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        return {"error": "Invalid JSON format from OpenAI"}

async def call_openai(query: str) -> Dict[str, Any]:
    """
    Calls OpenAI API and returns a properly parsed JSON response.
    """
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "You are a financial expert."},
                      {"role": "user", "content": query}],
            max_tokens=250
        )

        if not response or "choices" not in response or not response["choices"]:
            raise ValueError("Empty response from OpenAI API")

        response_text = response["choices"][0]["message"]["content"].strip()

        if not response_text:
            raise ValueError("OpenAI API returned an empty response")

        return extract_json(response_text)  # Extract only valid JSON

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return {"error": "OpenAI API error. Please try again later."}

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {"error": str(e)}

async def analyze_spending(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user's spending habits from a personal finance experts perspective.
    """
    user_data_clean = convert_objectid(user_data)

    query = f"""
    You are an expert financial advisor specializing in personal finance in India. 
    Your task is to provide precise, actionable financial insights based on clear financial metrics.
    For this section provide valuable and precise insights and ratings.

    ### User Data
    {json.dumps(user_data_clean, indent=2)}

    ### **Rules for Optimization**
    - **Overall User Spending Rating**(every financial consumption pattern of user) Understand user budget and give a rating out of '100' , **Important** Only give '100' rating to a 'perfect' budget allocation for given monthly income 
    - **Analysis** (deeper analysis of financially important metrics) **CAN BE BOTH NEGATIVE AND POSITIVE** based on user spendings.
    - **Primary Goal:** analyze the good and bad practices in the users expenditure habits and give discrete informative insights .
    - **Finally:** populate the data into the given JSON format strictly .

    ### **Expected JSON Output Format**
    Return **only** JSON in the following format:
    {{
        "rating": int,
        "analysis": [
            "Insight 1",
            "Insight 2",
            "Insight 3"
        ]
    }}

    Provide only the JSON response.
    """

    return await call_openai(query)

async def generate_longterm_goals(spend_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user's spending habits from a personal finance experts perspective.
    """
    query = f"""
    Based on the following spending analysis insights, generate long-term financial goals.

    ### Spending Analysis
    {json.dumps(spend_analysis, indent=2)}

    ### Expected JSON Output Format
    {{
        "longterm_goals": [
            "Goal 1",
            "Goal 2",
            "Goal 3"
        ]
    }}

    Provide only the JSON response.
    """

    return await call_openai(query)

async def generate_shortterm_goals(spend_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate short-term financial goals using OpenAI based on spending analysis.
    """
    query = f"""
    Based on the following spending analysis insights, generate short-term financial goals.

    ### Spending Analysis
    {json.dumps(spend_analysis, indent=2)}

    ### Expected JSON Output Format
    {{
        "shortterm_goals": [
            "Goal 1",
            "Goal 2",
            "Goal 3"
        ]
    }}

    Provide only the JSON response.
    """

    return await call_openai(query)

async def identify_good_habits(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identifies good financial practices and suggests strategic spending for growth.
    Returns a list with at most 4 key recommendations.
    """
    user_data_clean = convert_objectid(user_data)  # ✅ Convert MongoDB ObjectId

    query = f"""
    You are an expert financial advisor specializing in personal finance in India.
    Identify **positive financial habits** and areas where **strategic spending** can improve financial health.

    ### User Data
    {json.dumps(user_data_clean, indent=2)}

    ### Expected JSON Output Format
    {{
      "positiveSpendingOpportunities": {{
        "investments": [
          {{
            "category": "string",
            "recommendedIncrease": 0,
            "expectedReturns": "string"
          }}
        ],
        "selfDevelopment": [
          {{
            "area": "string",
            "suggestedAllocation": 0,
            "potentialBenefits": []
          }}
        ],
        "protectiveSpending": [
          {{
            "type": "string",
            "recommendedCoverage": 0,
            "justification": "string"
          }}
        ],
        "growthAreas": {{
          "skillEnhancement": [
            {{
              "skill": "string",
              "investmentNeeded": 0,
              "careerImpact": "string"
            }}
          ]
        }}
      }}
    }}

    **Return only valid JSON without explanations.**
    """

    try:
        # ✅ Call OpenAI API
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            temperature=0.6,
            top_p=0.9,
            messages=[
                {"role": "system", "content": "You are a financial expert."},
                {"role": "user", "content": query}
            ],
            max_tokens=500
        )

        # ✅ Extract response text
        response_text = response["choices"][0]["message"]["content"].strip()

        if not response_text:
            raise ValueError("OpenAI API returned an empty response")

        print(f"RAW OPENAI RESPONSE: {response_text}")  # ✅ Debugging: Print full OpenAI response

        # ✅ Use extract_json() to parse safely
        parsed_response = extract_json(response_text)

        if "error" in parsed_response:
            raise ValueError(f"OpenAI JSON extraction failed: {parsed_response['error']}")

        # ✅ Extract key areas and limit to at most 4 items
        extracted_list = []
        for key in ["positiveSpendingOpportunities", "growthAreas"]:
            if key in parsed_response:
                for sub_key, items in parsed_response[key].items():
                    if isinstance(items, list):  # ✅ Ensure it's a list before slicing
                        extracted_list.extend(items[:1])  # ✅ Pick only the most relevant from each section

        return extracted_list[:4]  # ✅ Ensure the final list has at most 4 elements

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return [{"error": "OpenAI API error. Please try again later."}]
    except json.JSONDecodeError:
        print("JSON decoding error from OpenAI response.")
        return [{"error": "Invalid JSON format from OpenAI"}]
    except Exception as e:
        print(f"Error in identifying good habits: {e}")
        return [{"error": str(e)}]



async def generate_insights(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate overall insights based on user financial data.
    """
    query = f"""PLACEHOLDER_PROMPT"""  # 🔴 Waiting for your prompt!
    return await call_openai(query)

async def identify_bad_habits(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identifies financial habits that need optimization and provides actionable reduction strategies.
    Returns a list with at most 4 key recommendations.
    """
    user_data_clean = convert_objectid(user_data)  # ✅ Convert MongoDB ObjectId

    query = f"""
    You are a professional financial advisor specializing in personal finance in India.
    Analyze **negative financial habits** and provide **clear, strategic improvement suggestions**.
    
    **Focus Areas**:
    1. Identify **unnecessary spending** that can be reduced.
    2. Highlight **inefficient debt management** and refinancing opportunities.
    3. Suggest **cost-effective lifestyle changes** that improve financial health.
    4. Recommend **utility savings** techniques for reducing monthly bills.

    ### User Data
    {json.dumps(user_data_clean, indent=2)}

    ### Expected JSON Output Format
    {{
      "highImpactReductions": [
        {{
          "category": "string",
          "currentSpending": 0,
          "recommendedSpending": 0,
          "potentialMonthlySavings": 0,
          "specificActions": [],
          "difficultyLevel": "EASY|MEDIUM|HARD"
        }}
      ],
      "debtOptimizations": [
        {{
          "loanType": "string",
          "currentEMI": 0,
          "optimizationStrategy": "string",
          "potentialSavings": 0
        }}
      ],
      "lifestyleAdjustments": [
        {{
          "habit": "string",
          "currentCost": 0,
          "alternative": "string",
          "monthlySavings": 0,
          "impactOnQualityOfLife": "LOW|MEDIUM|HIGH"
        }}
      ],
      "smartSubstitutions": [
        {{
          "currentItem": "string",
          "suggestedAlternative": "string",
          "upfrontCost": 0,
          "monthlySavings": 0,
          "breakEvenPeriod": "string"
        }}
      ]
    }}

    **Ensure the JSON response is properly formatted. Do not leave any values incomplete.**
    **Avoid truncation and always return a fully valid JSON response.**
    """

    try:
        # ✅ Call OpenAI API
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            temperature=0.6,
            top_p=0.9,
            messages=[
                {"role": "system", "content": "You are a financial expert."},
                {"role": "user", "content": query}
            ],
            max_tokens=600  # ✅ Increased for full JSON output
        )

        # ✅ Extract response text
        response_text = response["choices"][0]["message"]["content"].strip()

        if not response_text:
            raise ValueError("OpenAI API returned an empty response")

        print(f"RAW OPENAI RESPONSE: {response_text}")  # ✅ Debugging: Print full OpenAI response

        # ✅ Use extract_json() to parse safely
        parsed_response = extract_json(response_text)

        if "error" in parsed_response:
            raise ValueError(f"OpenAI JSON extraction failed: {parsed_response['error']}")

        # ✅ Extract key areas and limit to at most 4 items
        extracted_list = []
        for key in ["highImpactReductions", "debtOptimizations", "lifestyleAdjustments", "smartSubstitutions"]:
            if key in parsed_response:
                items = parsed_response[key]
                if isinstance(items, list) and len(items) > 0:  # ✅ Ensure it's a valid list before slicing
                    extracted_list.extend(items[:1])  # ✅ Pick only the most relevant from each section

        return extracted_list[:4] if extracted_list else [{"error": "No negative habits identified."}]

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return [{"error": "OpenAI API error. Please try again later."}]
    except json.JSONDecodeError:
        print("JSON decoding error from OpenAI response.")
        return [{"error": "Invalid JSON format from OpenAI"}]
    except Exception as e:
        print(f"Error in identifying bad habits: {e}")
        return [{"error": str(e)}]


