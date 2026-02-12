import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests

from app.models import SummarizeRequest, SummarizeResponse
from app.openrouter_client import OpenRouterClient

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Summarizer API Client")

# Initialize OpenRouter client at startup
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

openrouter_client = None

if OPENROUTER_API_KEY and OPENROUTER_MODEL:
    try:
        openrouter_client = OpenRouterClient(OPENROUTER_API_KEY, OPENROUTER_MODEL)
    except ValueError as e:
        print(f"Warning: Failed to initialize OpenRouter client: {e}")


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the service is running."""
    return HealthResponse(
        status="healthy",
        message="Service is running"
    )


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """
    Summarize the provided text using OpenRouter API.
    
    If OpenRouter is not configured, falls back to placeholder implementation.
    """
    # Check if OpenRouter client is available
    if openrouter_client is None:
        raise HTTPException(
            status_code=503,
            detail="OpenRouter API client not configured. Set OPENROUTER_API_KEY and OPENROUTER_MODEL environment variables."
        )
    
    try:
        # Call OpenRouter API for summarization
        result = openrouter_client.summarize(request.text, request.max_length)
        return SummarizeResponse(**result)
    
    except ValueError as e:
        # Input validation errors
        raise HTTPException(status_code=400, detail=str(e))
    
    except requests.RequestException as e:
        # API request failures
        raise HTTPException(
            status_code=502,
            detail=f"Failed to call OpenRouter API: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
