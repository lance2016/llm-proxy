from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import endpoints
import app.services.providers  # Import all providers

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to LLM API Gateway"} 