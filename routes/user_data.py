import json
from typing import Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, HTTPException
from config import MONGO_URI, MONGO_DB_NAME
from services.finance_ai import (
    analyze_spending,
    generate_longterm_goals,
    generate_shortterm_goals,
    identify_good_habits,
    identify_bad_habits
)

# ✅ Connect to MongoDB (Using AsyncIOMotorClient for async operations)
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db["users"]

router = APIRouter()

def convert_objectid(obj):
    """Convert MongoDB ObjectId to string recursively in dictionaries/lists."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    return obj

async def analyze_and_update_user(user: Dict[str, Any]):
    """
    Runs financial analyses, updates MongoDB, and includes debugging checks.
    """
    email = user.get("email", "No Email")
    print(f"📢 Fetching user data for: {email}")

    # ✅ Convert ObjectId to string for safe serialization
    user_clean = convert_objectid(user)
    print(f"📊 User's existing data: {json.dumps(user_clean, indent=2)}")

    # ✅ Run financial analyses with debugging
    try:
        spend_analysis = await analyze_spending(user_clean)
        print(f"✅ Spending Analysis: {spend_analysis}")
    except Exception as e:
        print(f"❌ Error in Spending Analysis: {e}")
        spend_analysis = user.get("spend_analysis", {})

    try:
        longterm = await generate_longterm_goals(spend_analysis)
        print(f"✅ Long-term Goals: {longterm}")
    except Exception as e:
        print(f"❌ Error in Long-term Goals: {e}")
        longterm = user.get("longterm", {})

    try:
        shortterm = await generate_shortterm_goals(spend_analysis)
        print(f"✅ Short-term Goals: {shortterm}")
    except Exception as e:
        print(f"❌ Error in Short-term Goals: {e}")
        shortterm = user.get("shortterm", {})

    try:
        good_habits = await identify_good_habits(user_clean)
        print(f"✅ Good Habits: {good_habits}")
    except Exception as e:
        print(f"❌ Error in Good Habits: {e}")
        good_habits = user.get("good_habits", [])

    try:
        bad_habits = await identify_bad_habits(user_clean)
        print(f"✅ Bad Habits: {bad_habits}")
    except Exception as e:
        print(f"❌ Error in Bad Habits: {e}")
        bad_habits = user.get("bad_habits", [])

    # ✅ Preserve existing data while updating only new values
    update_data = {
        "spend_analysis": spend_analysis or user.get("spend_analysis", {}),
        "longterm": longterm or user.get("longterm", {}),
        "shortterm": shortterm or user.get("shortterm", {}),
        "good_habits": good_habits or user.get("good_habits", []),
        "bad_habits": bad_habits or user.get("bad_habits", [])
    }

    # ✅ Update MongoDB without erasing old data
    await users_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": update_data}
    )
    print("📁 Updated MongoDB successfully!")

    # ✅ Fetch updated user document
    updated_user = await users_collection.find_one({"_id": ObjectId(user["_id"])})

    return {
        "message": "Analysis completed and updated",
        "email": updated_user.get("email"),
        "data": convert_objectid(updated_user)
    }

@router.get("/user/verify/{user_id}")
async def verify_and_run_analysis(user_id: str):
    """
    Fetches email based on `_id`, verifies, runs analysis, and updates DB.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectID format")

    # ✅ Fetch user data asynchronously (Fixed: No 'await' error)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    email = user.get("email")
    if not email:
        raise HTTPException(status_code=404, detail="User email not found")

    print(f"✅ User found: {email}")

    # ✅ Run analysis and update
    result = await analyze_and_update_user(user)

    # ✅ Print result for debugging
    print(json.dumps(result, indent=2))

    return result

@router.delete("/user/{user_id}")
async def delete_user(user_id: str):
    """
    Deletes a user from MongoDB based on `_id`.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectID format")

    result = await users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    print(f"🗑️ User with _id {user_id} deleted successfully!")

    return {"message": "User deleted successfully"}
