agents.md — Backend API Contract
## Backend API Contract
The backend is a FastAPI service running locally on port 8000.
### Endpoint
- POST /summarize
### Request JSON
‘‘‘json
{
"text": "string (required, non-empty)",
"max_length": "integer (optional, default = 100)"
}
{
"summary": "string",
"model": "string",
"truncated": "boolean"
}