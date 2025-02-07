from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS middleware
from routes import user_data, analysis, recommendations, chat

app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any domain (you can restrict this)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers (Authorization, Content-Type, etc.)
)


# ✅ Include API routes
app.include_router(user_data.router, prefix="/user")
app.include_router(analysis.router, prefix="/analysis")
# app.include_router(goals.router, prefix="/goals")
app.include_router(recommendations.router, prefix="/recommendations")
app.include_router(chat.router, prefix="/chat")


# ✅ Root endpoint to check API health
@app.get("/")
async def root():
    return {"message": "API is running!"}
