import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

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
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=genai.GenerationConfig())

    chat = model.start_chat(history=chat_history)
    response = chat.send_message(messages[-1]["content"])
    return response.text


def get_gemini_response_stream(messages):
    # Prepare messages for Gemini API
    chat_history = []
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append({"role": "user", "parts": [msg["content"]]})
        else:
            chat_history.append({"role": "model", "parts": [msg["content"]]})
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=genai.GenerationConfig())
    chat = model.start_chat(history=chat_history)
    # Use stream=True to get a generator of chunks
    return chat.send_message(messages[-1]["content"], stream=True)


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
                    response_stream = get_gemini_response_stream(st.session_state["messages"])
                    full_response = ""
                    response_placeholder = st.empty()
                    animation_chars = [" ░", " ▒", " ▓", " █", " ▓", " ▒", " ░"]
                    anim_idx = 0
                    for chunk in response_stream:
                        if hasattr(chunk, 'text'):
                            for char in chunk.text:
                                full_response += char
                                # Add a blinking cursor and animated bar
                                anim = animation_chars[anim_idx % len(animation_chars)]
                                response_placeholder.markdown(full_response + f'<span style="color:#fcba03;font-weight:bold;">|{anim}</span>', unsafe_allow_html=True)
                                anim_idx += 1
                                time.sleep(0.025)  # Smooth animation
                    # Finalize response without animation
                    response_placeholder.markdown(full_response)
                    st.session_state["messages"].append({"role": "model", "content": full_response})
                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.session_state["messages"].append({"role": "model", "content": error_msg})
                    st.markdown(error_msg)
        st.rerun()


if __name__ == "__main__":
    main()
