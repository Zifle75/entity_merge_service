import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.models import MergeCompaniesRequest, MergeCompaniesResponse
from app.repository import SqliteRepository
from app.service import MergeService

# Load environment variables from .env file.
load_dotenv()

# Path to database file relative to project root.
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/entity_merge.db")

# Create web API application instance
app = FastAPI(title="Entity Merge Service", version="0.1.0")

# Creates DAO to talk to SQLite database
repo = SqliteRepository(database_path=DATABASE_PATH)

# Creates the business-logic layer and injects the repository/DAO into it.
service = MergeService(repo=repo)

# API endpoint for merging companies. Delegates to service layer to do the work.
@app.post("/v1/company-merges", response_model=MergeCompaniesResponse)
async def merge_companies(request: MergeCompaniesRequest) -> MergeCompaniesResponse:
    return await service.merge_companies(request)

# Simple health check endpoint to verify service is running.
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
