import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"bypass\s+(all\s+)?(safety|security)\s+filters",
    r"tell\s+me\s+(the|your)\s+api\s*key",
    r"what\s+is\s+(the|your)\s+api\s*key",
]


def validate_user_input(prompt: str) -> str:
  for pattern in INJECTION_PATTERNS:
    if re.search(pattern, prompt, re.IGNORECASE):
      raise ValueError(
          "Potential prompt injection detected. Request blocked by Input"
          " Guardrail."
      )
  return prompt