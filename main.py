import os
import sys
from ConversationManager import ConversationManager

# 1. Put your key here (or export it in terminal via export GROQ_API_KEY="...")
MY_API_KEY = "Insert_your_API_key"

def main():
    # Fallback to environment variable if MY_API_KEY is left as placeholder
    api_key = os.getenv("GROQ_API_KEY", MY_API_KEY)

    # 2. Pass api_key directly into ConversationManager
    chatbot_brain = ConversationManager(
        api_key=api_key,
        system_prompt="You are a sarcastic but helpful engineering assistant."
    )
    
    print("AI Chatbot Initialized! Type 'quit' or 'exit' to stop.")
    print("------------------------------------------------------")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit"]:
                print("AI: Goodbye!")
                break
                
            if not user_input:
                continue

            # 3. Add user message (triggers input guardrails)
            chatbot_brain.add_user_message(user_input)

            # 4. Generate response (runs MCP tools, RAG, and Pydantic validation)
            response = chatbot_brain.generate_response()

            # 5. Save response to conversation history
            chatbot_brain.add_ai_message(response)

            # 6. Display output & metadata
            print(f"\nAI: {response.response_text}")
            print(f"  [Intent: {response.detected_intent} | Confidence: {response.confidence_score * 100:.1f}%]")

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()