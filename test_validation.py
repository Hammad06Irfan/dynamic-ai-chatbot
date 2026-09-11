import os
from openai import OpenAI
import instructor
from schemas import ChatbotResponse

# Patch the standard client with Instructor
GROQ_KEY = "Insert_your_API_key"
raw_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_KEY
)
client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON)

user_message = "Can you explain how a common-drain amplifier works and its typical output impedance?"

# The API call enforces the Pydantic model
validated_output: ChatbotResponse = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    response_model=ChatbotResponse,
    messages=[
        {"role": "system", "content": "You are a precise technical tutor."},
        {"role": "user", "content": user_message}
    ],
    temperature=0.2
)

# Inspect the validated data attributes
print(f"Response: {validated_output.response_text}\n")
print(f"Intent: {validated_output.detected_intent}")
print(f"Confidence: {validated_output.confidence_score}")
print(f"Topics: {validated_output.key_topics}")