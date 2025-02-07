from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_NAME, MONGO_URI

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections
users_collection = db["users"]
object_collection = db["users"]