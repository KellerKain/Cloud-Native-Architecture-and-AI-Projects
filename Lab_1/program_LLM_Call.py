import os
import requests
API_KEY = os.getenv("API_KEY", "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")
MODEL = "x-ai/grok-code-fast-1"
def call_model(prompt: str):
    # Invoke the AI service via OpenRouter API
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        },
    )
    return response.json()
if __name__ == "__main__":
    result = call_model("Explain cloud-native systems in a bullet point summary.")
    content = result["choices"][0]["message"]["content"]
    print(content)
    print(f"\nLength of returned text: {len(content)} characters")
    