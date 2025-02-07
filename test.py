import asyncio
import json
from typing import Dict, Any
from bson import ObjectId
from pymongo import MongoClient
from fastapi import HTTPException
from config import MONGO_URI, MONGO_DB_NAME
from services.finance_ai import (
    analyze_spending,
    generate_longterm_goals,
    generate_shortterm_goals,
    identify_good_habits,
    identify_bad_habits
)

# ✅ Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db["users"]

def convert_objectid(obj):
    """Convert MongoDB ObjectId to string recursively in dictionaries/lists."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    return obj

def analyze_and_update_user(user: Dict[str, Any]):
    """
    Runs extreme financial analyses, considers all input fields discretely and updates MongoDB.
    """
    email = user.get("email", "No Email")

    # ✅ Convert ObjectId to string to avoid serialization error
    user_clean = convert_objectid(user)

    # ✅ Print debug info
    print(f"📢 Fetching user data for: {email}")
    print(f"📊 User's existing data: {json.dumps(user_clean, indent=2)}")  # No more serialization issues

    # ✅ Run financial analyses
    spend_analysis = asyncio.run(analyze_spending(user_clean))
    longterm = asyncio.run(generate_longterm_goals(spend_analysis))
    shortterm = asyncio.run(generate_shortterm_goals(spend_analysis))
    good_habits = asyncio.run(identify_good_habits(user_clean))
    bad_habits = asyncio.run(identify_bad_habits(user_clean))

    # ✅ Preserve existing data while updating only new values
    update_data = {
        "spend_analysis": spend_analysis or user.get("spend_analysis", {}),
        "longterm": longterm or user.get("longterm", {}),
        "shortterm": shortterm or user.get("shortterm", {}),
        "good_habits": good_habits or user.get("good_habits", []),
        "bad_habits": bad_habits or user.get("bad_habits", [])
    }

    # ✅ Update MongoDB with new computed values
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": update_data}
    )

    # ✅ Fetch updated user document
    updated_user = users_collection.find_one({"_id": user["_id"]})

    return {
        "message": "Analysis completed and updated",
        "email": updated_user.get("email"),
        "data": convert_objectid(updated_user)  # ✅ Convert ObjectId before returning
    }


def analyze_user(user_id: str):
    """
    Fetches full user data based on _id, verifies email, runs intricate financial analysis, and updates MongoDB with precise statistics and data.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectID format")

    # ✅ Fetch full user document from MongoDB
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    email = user.get("email")
    if not email:
        raise HTTPException(status_code=404, detail="User email not found")

    print(f"✅ User found: {email}")

    # ✅ Run analysis and update
    result = analyze_and_update_user(user)
    print("📁 Updated MongoDB successfully!")

    # ✅ Print result for debugging
    print(json.dumps(result, indent=2))

    return result


# ✅ Run the script (For testing)
if __name__ == "__main__":
    user_id_input = input("Enter user _id: ").strip()
    analyze_user(user_id_input)
