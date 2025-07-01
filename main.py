import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def get_gemini_response(messages):
    # Prepare messages for Gemini API
    chat_history = []
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append({"role": "user", "parts": [msg["content"]]})
        else:
            chat_history.append({"role": "model", "parts": [msg["content"]]})
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(messages[-1]["content"])
    return response.text


def main():
    st.title("Python Chat App")

    # Display chat messages using st.chat_message
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # Use st.chat_input for user input
    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Gemini is typing..."):
                try:
                    gemini_response = get_gemini_response(st.session_state["messages"])
                    st.session_state["messages"].append(
                        {"role": "model", "content": gemini_response}
                    )
                    st.markdown(gemini_response)
                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.session_state["messages"].append(
                        {"role": "model", "content": error_msg}
                    )
                    st.markdown(error_msg)
        st.rerun()


if __name__ == "__main__":
    main()
