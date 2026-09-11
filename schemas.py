import re
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class ChatbotResponse(BaseModel):
  """Deterministic validation schema with active output guardrails."""

  response_text: str = Field(
      description="The primary conversational response delivered to the user."
  )
  detected_intent: Literal[
      "question", "chitchat", "instruction", "complaint", "other"
  ] = Field(
      description="Categorization of what the user is trying to accomplish."
  )
  confidence_score: float = Field(
      ge=0.0, le=1.0, description="Confidence in answering the query."
  )
  key_topics: List[str] = Field(
      default_factory=list,
      description="List of 1 to 4 extracted subject keywords.",
  )

  @field_validator("response_text")
  @classmethod
  def guardrail_output(cls, value: str) -> str:
    # 1. Leakage Guardrail: Strict check for Groq secret keys
    if re.search(r"gsk_[a-zA-Z0-9]{20,}", value):
      raise ValueError(
          "SECURITY POLICY VIOLATION: Model attempted to leak an API key."
      )

    # 2. Email Masking: Strict email syntax
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    sanitized = re.sub(email_pattern, "[REDACTED_EMAIL]", value)

    # 3. Phone Masking: Must have explicit standard delimiters (e.g., 555-123-4567 or (555) 123-4567)
    # This prevents mathematical expressions like '12 - 5' or '200' from matching.
    phone_pattern = r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"
    sanitized = re.sub(phone_pattern, "[REDACTED_PHONE]", sanitized)

    return sanitized