from uuid import uuid4
import streamlit as st
from client import APIClient

# Initialize the API client
base_url = "http://127.0.0.1:5000"  # Update with the actual base URL if different
client = APIClient(base_url)

# Streamlit UI
st.title("Chat with LLM")

# Session state to store the conversation
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Save the thread ID in session state
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = uuid4()

# Input box for user message
if 'user_message' not in st.session_state:
    st.session_state.user_message = ''
def submit():
    st.session_state.user_message = st.session_state.widget
    st.session_state.widget = ''

user_input = st.text_input("Ask LLM:", key='widget')

# Send button
if st.button("Send", on_click=submit):
    input_message = st.session_state.user_message.strip()
    if input_message:
        # Call the API client
        response = client.query(input_message, thread_id=st.session_state["thread_id"])

        # Display the response
        if "error" in response:
            st.error(f"Error: {response['error']}")
        else:
            if "thread_id" not in st.session_state:
                st.session_state["thread_id"] = response.get("thread_id", "THREADID_ERROR")  # Save thread ID
            reply = response.get("response", "No response")

            # Update session state
            st.session_state["messages"].append(("You", input_message))
            st.session_state["messages"].append(("LLM", reply))


# Display the conversation
for sender, message in st.session_state["messages"]:
    st.write(f"**{sender}:** {message}")

