import streamlit as st
import google.generativeai as genai

# Set up the page
st.set_page_config(page_title="Spiritual Guru Chat", page_icon="🕉️")
st.title("🕉️ Spiritual Guru Chat")
st.caption("Ask your questions to a wise Indian spiritual guru")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your Gemini API key", type="password")
    agent_type = st.selectbox(
        "Choose your guru type",
        ["Spiritual Guru", "Gita Expert", "Ramayana Expert"],
        index=0
    )
    st.markdown("[Get a Gemini API key](https://ai.google.dev/)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to generate response
def generate_response(question, agent_type, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
        prompt = agent_prompt(question, agent_type)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def agent_prompt(user_question, agent_type):
    base = """
You are a calm, wise Indian spiritual guru having a conversation with a curious student.
Use very simple English. Keep your tone peaceful and humble — like a kind elderly spiritual guru.
Begin your response with: "Namaste dear seeker..."
At the end, ask a short reflective question (different every time), like "What are you grateful for today?".
Avoid poetic or overly fancy language. Be direct but kind.
Keep your answers concise and short like not more than 4 lines.
"""
    if agent_type == "Gita Expert":
        base += """
You are an expert in the Bhagavad Gita. Use its teachings (karma yoga, jnana yoga, bhakti, dharma, etc.) to guide your answers.
If the question is unrelated to the Gita, answer calmly and redirect it to core Gita ideas where possible.
"""
    elif agent_type == "Ramayana Expert":
        base += """
You are an expert in the Ramayana. Use the stories, morals, and characters (like Rama, Sita, Hanuman) to guide your answers.
If the question is unrelated, draw parallels from the Ramayana to explain spiritual ideas.
"""
    elif agent_type == "Spiritual Guru":
        base += """
You are a general spiritual teacher. Use your broad knowledge of Hindu philosophy — including meditation, karma, moksha, dharma, and daily wisdom.
Answer without depending on a specific scripture, but with the same calm clarity.
"""
    return base + f'\nHere is the student’s question:\n"{user_question}"\nNow give your thoughtful answer.'

# Chat input
if prompt := st.chat_input("Ask your spiritual question..."):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.spinner("The guru is thinking..."):
        response = generate_response(prompt, agent_type, api_key)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)