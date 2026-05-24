import os
from dotenv import load_dotenv

# Load environment variables from api/.env file at startup
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY for the google-genai library
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.agents import router as agents_router


app = FastAPI(
    title="content_creator Agent Server",
    version="0.1.0",
    description="Dedicated agent runner server communicating with Frontend.",
)

# Allow browser clients from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router)
