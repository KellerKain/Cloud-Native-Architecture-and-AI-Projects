from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    """Request schema for the /summarize endpoint."""
    text: str = Field(..., description="The text to summarize (required, non-empty)")
    max_length: int = Field(default=100, description="Maximum length of the summary (optional, default=100)", ge=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text is non-empty after stripping whitespace."""
        if not v or not v.strip():
            raise ValueError("text must be a non-empty string")
        return v.strip()


class SummarizeResponse(BaseModel):
    """Response schema for the /summarize endpoint."""
    summary: str = Field(..., description="The generated summary")
    model: str = Field(..., description="The model used to generate the summary")
    truncated: bool = Field(..., description="Whether the summary was truncated")
