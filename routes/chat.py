from fastapi import APIRouter
#from models import ChatMessage
import openai
from config import OPENAI_API_KEY

router = APIRouter()
openai.api_key = OPENAI_API_KEY

# @router.post("/chat/")
# async def chat_with_ai(chat_message: ChatMessage):
#     response = openai.Completion.create(
#         engine="text-davinci-003",
#         prompt=chat_message.message,
#         max_tokens=100
#     )
#     return {"response": response.choices[0].text.strip()}