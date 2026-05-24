import os
from dotenv import load_dotenv

# Load environment variables from api/.env file at startup
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.insights import router as insights_router
from app.routes.internal_tools import router as internal_tools_router
from app.routes.projects import router as projects_router


app = FastAPI(
    title="content_creator API",
    version="0.1.0",
    description="FastAPI boundary for the real estate AI marketing content MVP.",
)

# Allow browser clients from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(projects_router)
app.include_router(insights_router)
app.include_router(internal_tools_router)
