import os
import streamlit as st
from ConversationManager import ConversationManager

st.set_page_config(page_title="AI Engineering Assistant", page_icon="🤖", layout="centered")
st.title("🤖 AI Engineering Assistant")

# 1. Initialize ConversationManager once in session_state
if "manager" not in st.session_state:
    api_key = "Insert_your_API_key_here"
    st.session_state.manager = ConversationManager(api_key=api_key)

manager: ConversationManager = st.session_state.manager

# 2. Sidebar for Persona & History Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    user_persona = st.text_area(
        "System Persona",
        value=manager.system_prompt,
        help="Updating this changes the system instruction and resets history."
    )
    # Check if the user changed the persona in the UI
    if user_persona != manager.system_prompt:
        manager.set_system_prompt(user_persona)
        st.rerun()

    if st.button("Clear Conversation", use_container_width=True):
        manager.clear_history()
        st.rerun()

# 3. Render Conversation History & Telemetry Badges
for msg in manager.get_messages():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If the turn includes schema metadata, display it
        if "metadata" in msg:
            meta = msg["metadata"]
            with st.expander("🔍 Guardrail & Schema Telemetry"):
                st.caption(f"**Intent:** `{meta['intent']}` | **Confidence:** `{meta['confidence'] * 100:.1f}%`")
                st.caption(f"**Topics:** {', '.join(meta['topics'])}")

# 4. Handle User Input
if user_prompt := st.chat_input("Ask a question..."):
    try:
        # Step A: Validate input via guardrail and append to history
        manager.add_user_message(user_prompt)
        st.chat_message("user").markdown(user_prompt)

        # Step B: Generate structured response via Groq + Instructor
        with st.chat_message("assistant"):
            with st.spinner("Validating & generating..."):
                response_obj = manager.generate_response()
                manager.add_ai_message(response_obj)

            # Step C: Render validated output & metadata
            st.markdown(response_obj.response_text)
            with st.expander("🔍 Guardrail & Schema Telemetry", expanded=True):
                st.caption(f"**Intent:** `{response_obj.detected_intent}` | **Confidence:** `{response_obj.confidence_score * 100:.1f}%`")
                st.caption(f"**Topics:** {', '.join(response_obj.key_topics)}")

    except ValueError as e:
        # Catches Input Guardrail prompt injection rejections
        st.error(f"🛡️ **Security Alert:** {e}")