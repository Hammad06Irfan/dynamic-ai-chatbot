import streamlit as ui
from openai import OpenAI
from ConversationManager import ConversationManager
# Assuming your ConversationManager class is defined here, or imported:
# from conversation_manager import ConversationManager

# 1. Page Configuration (Sets up the browser tab title and layout)
ui.set_page_config(page_title="Dynamic AI Chatbot", page_icon="🤖", layout="centered")
ui.title("🤖 My Dynamic AI Chatbot")
ui.caption("Powered by Groq & Streamlit")

# 2. Initialize the ConversationManager inside Streamlit's Session State (Memory)
# This ensures it only gets created ONCE per browser session.
if "chatbot_brain" not in ui.session_state:
    ui.session_state.chatbot_brain = ConversationManager(
        system_prompt="You are a brilliant, slightly sarcastic AI assistant living inside a sleek web interface."
    )

# 3. Initialize the Groq Client
if "client" not in ui.session_state:
    ui.session_state.client = OpenAI(
        api_key="APIKEY",           # Swap this with your actual key
        base_url="https://api.groq.com/openai/v1"   # Routes to Groq
    )

# 4. Create a Sidebar with a Reset Button
# 4. Create a Sidebar with Persona Selector & Reset Button
with ui.sidebar:
    ui.header("Chat Settings")
    
    # Create a text input box for the custom persona
    custom_persona = ui.text_input(
        label="AI Persona / Instructions:",
        value="You are a brilliant, slightly sarcastic AI assistant living inside a sleek web interface."
    )
    
    # Check if the text in the box is DIFFERENT from the current system prompt
    # We grab the current prompt safely from our manager's history list
    current_prompt = ui.session_state.chatbot_brain.get_history()[0]["content"]
    
    if custom_persona != current_prompt:
        # If the user typed something new, update the brain and restart the session
        ui.session_state.chatbot_brain.update_system_prompt(custom_persona)
        ui.success("Persona updated! Chat reset.")
        ui.rerun()

    ui.markdown("---") # Draw a clean line in the sidebar
    ui.subheader("Controls")
    # If the user manually clicks 'Clear Chat', wipe the history and refresh the page
    if ui.button("Clear Chat History", type="primary"):
        ui.session_state.chatbot_brain.clear_history()
        ui.rerun()

# 5. Display the Past Chat History on the Screen
# Streamlit looks at our manager's list and draws the correct bubbles
for msg in ui.session_state.chatbot_brain.get_history():
    # Skip displaying the secret system prompt to the user
    if msg["role"] == "system":
        continue
        
    # Use Streamlit's native chat bubble styling
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with ui.chat_message(msg["role"], avatar=avatar):
        ui.write(msg["content"])

# 6. Handle New User Input
# ui.chat_input automatically places a beautiful input bar at the bottom of the page
if user_input := ui.chat_input("Say something to your AI..."):
    
    # Immediately show the user's message on the screen
    with ui.chat_message("user", avatar="🧑‍💻"):
        ui.write(user_input)
        
    # Save the message to our manager's history
    ui.session_state.chatbot_brain.add_user_message(user_input)

    # 7. Call the Groq API and get the response
    with ui.chat_message("assistant", avatar="🤖"):
        # Create a nice spinning status loader while waiting for the API
        with ui.spinner("Thinking..."):
            try:
                response = ui.session_state.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=ui.session_state.chatbot_brain.get_history()
                )
                ai_response = response.choices[0].message.content
                
                # Render the AI's response on the screen
                ui.write(ai_response)
                
                # Save the AI's response to history
                ui.session_state.chatbot_brain.add_ai_message(ai_response)
                
            except Exception as e:
                ui.error(f"An error occurred: {e}")