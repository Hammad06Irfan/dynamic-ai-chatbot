import os
from openai import OpenAI
from ConversationManager import ConversationManager
# Assuming your ConversationManager class is in the same file or imported
# from conversation_manager import ConversationManager

# 1. Initialize the OpenAI client (It automatically looks for an OPENAI_API_KEY environment variable)
client = OpenAI(
    api_key="APIKEY",           # Your gsk_ key
    base_url="https://api.groq.com/openai/v1"  # Tells the library to route to Groq
)

def main():
    # 2. Instantiate your conversation manager
    chatbot_brain = ConversationManager(system_prompt="You are a sarcastic but helpful assistant.")
    
    print("AI Chatbot Initialized! Type 'quit' or 'exit' to stop.")
    print("--------------------------------------------------")

    while True:
        # 3. Take user input
        user_input = input("\nYou: ")
        
        # Check if the user wants to break out of the loop
        if user_input.lower() in ["quit", "exit"]:
            print("AI: Goodbye!")
            break
            
        if not user_input.strip():
            continue

        # 4. Save the user's message to our manager's history
        chatbot_brain.add_user_message(user_input)

        try:
            # 5. Send the entire conversation history to OpenAI
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # A fast, cheap, and smart model perfect for projects
                messages=chatbot_brain.get_history() # Passing the full array of history!
            )

            # 6. Extract the AI's text response
            ai_response = response.choices[0].message.content
            print(f"\nAI: {ai_response}")

            # 7. CRITICAL: Save the AI's response to history so it remembers it next turn!
            chatbot_brain.add_ai_message(ai_response)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()