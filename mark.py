import streamlit as st
from utils.llm_client import get_completion
from utils.log_utils import logger
from prompt.prompts import system_prompt, market_insights
import pandas as pd

# Streamlit UI
st.set_page_config(page_title='MARK', page_icon="👨‍💻")
st.title("MARK - Your Personal Coach!")
st.divider()

# Initialize session state for conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []
if "messages_updated" not in st.session_state:
    st.session_state.messages_updated = False
if "context_mode" not in st.session_state:
    st.session_state.context_mode = False
if "stored_text" not in st.session_state:
    st.session_state.stored_text = ""

# Function to add new messages
def add_to_conversation(user_input, bot_response):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

def enable_context_mode():
    st.session_state.context_mode = True

def store_text():
    if st.session_state.input_text:
        st.session_state.stored_text = st.session_state.input_text
        st.session_state.context_mode = False  # Disable context mode after storing


# Function to edit the last conversation
def edit_last_conversation():
    if len(st.session_state.messages) < 2:
        st.warning("No conversation to edit!")
        return

    last_user_msg = st.session_state.messages[-2]["content"]
    last_bot_msg = st.session_state.messages[-1]["content"]

    edited_user_msg = st.text_area("Edit User Message:", value=last_user_msg, key="edit_user")
    edited_bot_msg = st.text_area("Edit Bot Response:", value=last_bot_msg, key="edit_bot")

    if st.button("Submit Edited Conversation"):
        st.session_state.messages[-2]["content"] = edited_user_msg
        st.session_state.messages[-1]["content"] = edited_bot_msg
        st.session_state.messages_updated = True
        st.markdown(
            """<style>.custom-alert {position: fixed; bottom: 10px; right: 10px; width: auto; z-index: 9999; background-color: #d4edda; color: #155724; padding: 10px; text-align: center; font-size: 16px; border-radius: 5px; opacity: 1;}</style><div class="custom-alert" id="custom-alert">Last conversation updated!</div>""",
            unsafe_allow_html=True
        )

# Display chat messages
if not st.session_state.messages_updated:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    st.session_state.messages_updated = False
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.sidebar.title("About:")
st.sidebar.info("Welcome to the interface! Introducing MARK (Marketing Analytics and Results Coach), a highly intelligent and collaborative marketing assistant specializing in B2B tech products.")
st.sidebar.divider()

if not st.session_state.context_mode:
    st.sidebar.button("Add Context", on_click=enable_context_mode)

# If in context mode, display the text input and submit button
if st.session_state.context_mode:
    st.text_area("Tell me about your product:", key="input_text", value=st.session_state.stored_text)
    st.button("Submit", on_click=store_text)


st.sidebar.selectbox("Choose Industry", ["Tech", "TBD"])  # Add other industries as needed
st.sidebar.selectbox("Choose Persona", ["Marketing Leader", "TBD"])  # Add other personas as needed
wisdom = st.sidebar.toggle("Guided response")
st.sidebar.divider()

if user_input := st.chat_input("Input question"):
    # Display user message in chat container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare market_data based on the wisdom toggle
    market_data = market_insights if wisdom else ""
    context_data = st.session_state.stored_text  # Ensure this gets updated context


    # Build full prompt using context, conversation history, and modified system prompt
    full_prompt = system_prompt.format(
        market_data=market_data,
        conv_history="\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]),
        question=user_input,
        user_context=context_data  # Ensure context is passed correctly
    )

    # Get completion using the full prompt
    response = get_completion(full_prompt)

    # Display assistant response in chat container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

col1, col2, col3, col4 = st.columns([7, 1.2, 1.8, 1.2])
with col2:
    if st.button("Clear"):
        st.session_state.messages = []
        st.session_state.context_input = ""
        st.markdown(
            """<style>.custom-alert {position: fixed; bottom: 10px; right: 10px; width: auto; z-index: 9999; background-color: #d4edda; color: #155724; padding: 10px; text-align: center; font-size: 16px; border-radius: 5px; opacity: 1;}</style><div class="custom-alert" id="custom-alert">Chat history and context cleared!</div>""",
            unsafe_allow_html=True
        )


with col3:
    memory = f"User added context: \n{st.session_state.stored_text} \n"+"\n".join([f"{msg['role']}: {msg['content']}\n" for msg in st.session_state.messages])
    if st.download_button("Save chat!", memory, "MARK_conversation.txt"):
        st.markdown(
            """<style>.custom-alert {position: fixed; bottom: 10px; right: 10px; width: auto; z-index: 9999; background-color: #d4edda; color: #155724; padding: 10px; text-align: center; font-size: 16px; border-radius: 5px; opacity: 1;}</style><div class="custom-alert" id="custom-alert">Chat history saved!</div>""",
            unsafe_allow_html=True
        )

with col4:
    with st.popover("Edit this"):
        st.markdown("""
            <style>
                .stTextArea {
                    width: 100%;
                }
                .stPopover {
                    width: 100vw;
                    left: 0;
                }
            </style>
        """, unsafe_allow_html=True)
        edit_last_conversation()

# Custom styles
st.markdown("<style>body {background-color: #f0f2f6;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button {background-color: #004080; color: white;}</style>", unsafe_allow_html=True)
st.sidebar.image("Merkle_logo.png", width=100, use_container_width=True)
