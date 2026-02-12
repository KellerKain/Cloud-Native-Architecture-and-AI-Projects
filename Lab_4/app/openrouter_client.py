"""OpenRouter API client for text summarization."""
import requests
from typing import Optional


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, model: str):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier (e.g., "openai/gpt-3.5-turbo")
        
        Raises:
            ValueError: If api_key is empty
        """
        if not api_key or not api_key.strip():
            raise ValueError("OpenRouter API key cannot be empty")
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        self.api_key = api_key
        self.model = model

    def summarize(self, text: str, max_length: int = 100) -> dict:
        """
        Summarize text using OpenRouter API.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
        
        Returns:
            Dictionary with keys: summary, model, truncated
        
        Raises:
            ValueError: If text is empty
            requests.RequestException: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Prepare the prompt
        prompt = f"Summarize the following text in approximately {max_length} words or less:\n\n{text}"

        # Prepare request headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Prepare request body
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_length * 2,  # Approximate conversion: 1 token ~= 0.25 words
        }

        # Make the API request
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"OpenRouter API request failed: {str(e)}")

        # Parse the response
        data = response.json()

        # Extract the summary from the response
        if "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("Invalid response from OpenRouter API: no choices returned")

        summary = data["choices"][0]["message"]["content"].strip()

        # Check if truncation occurred by counting words
        summary_word_count = len(summary.split())
        truncated = summary_word_count > max_length

        return {
            "summary": summary,
            "model": self.model,
            "truncated": truncated
        }
