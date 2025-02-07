from fastapi import APIRouter, HTTPException
from bson import ObjectId  # ✅ Import ObjectId for MongoDB query
from services.finance_ai import analyze_spending
from models import User
from database import users_collection  # ✅ Import MongoDB collection from config.py

router = APIRouter()

@router.get("/analysis/{user_id}")
async def analyze_user_finances(user_id: str):
    """
    Fetches user financial data from MongoDB using `_id`, analyzes spending, and returns insights.
    """
    # ✅ Validate MongoDB ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectID format")

    # ✅ Fetch user data by `_id`
    user = await users_collection.find_one({"_id": ObjectId(user_id)}, {"financial": 1})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Extract financial data
    financial_data = user.get("financial", {})

    if not financial_data:
        raise HTTPException(status_code=400, detail="No financial data found for the user")

    # ✅ Analyze financial data using OpenAI GPT
    try:
        analysis_result = await analyze_spending(financial_data)

        return {
            "user_id": user_id,
            "analysis": analysis_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing financial data: {str(e)}")
