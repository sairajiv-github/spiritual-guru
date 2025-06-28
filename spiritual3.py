import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- Gemini setup ---
def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        chat_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        return chat_model
    except Exception as e:
        st.error(f"Failed to configure Gemini: {str(e)}")
        return None

# --- PDF Processing ---
def load_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text, max_tokens=300):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_tokens:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# --- TF-IDF Retrieval ---
@st.cache_data
def tfidf_indexing(chunks):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return vectorizer, tfidf_matrix

def find_similar_chunks(query, vectorizer, tfidf_matrix, chunks, top_k=3):
    query_vec = vectorizer.transform([query])
    cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(cosine_sim)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

# --- Guru Prompt Engineering ---
def build_prompt(query, retrieved_chunks, agent_type):
    intro = f"""
You are a calm Indian spiritual guru. Use the context below and your own wisdom to answer the student's question.
Start with: "Namaste dear seeker..."
End with a short reflective question (change it every time, like "What truth are you living today?".Remember it 
should be different everytime and it should be reflective in the context of the question asked and the answer given).
Use very simple, clear English. Avoid poetic or dramatic tone. Answer should be short and concise (max 4 lines).
Agent Type: {agent_type}
Question: {query}

Context:
"""
    for i, chunk in enumerate(retrieved_chunks, 1):
        intro += f"[{i}] {chunk}\n"
    intro += "\nNow answer the question based on the context and your knowledge."
    return intro

# --- Streamlit UI ---
st.title("📚🕉️ Spiritual Guru")

# Initialize session state
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'chat_model' not in st.session_state:
    st.session_state.chat_model = None

api_key = st.text_input("🔑 Enter Gemini API Key", type="password")
agent_type = st.selectbox("🧙‍♂️ Choose your expert", ["Gita Expert", "Ramayana Expert", "Spiritual Guru"])
uploaded_files = st.file_uploader("📂 Upload PDF (e.g., Gita.pdf)", type="pdf", accept_multiple_files=True)

# Configure Gemini only once
if api_key and not st.session_state.api_key_valid:
    st.session_state.chat_model = configure_gemini(api_key)
    if st.session_state.chat_model:
        st.session_state.api_key_valid = True
        st.success("API key validated successfully!")

# Process PDF and questions
if st.session_state.api_key_valid and uploaded_files:
    full_text = ""
    for file in uploaded_files:
        full_text += load_pdf_text(file)

    chunks = chunk_text(full_text)
    vectorizer, tfidf_matrix = tfidf_indexing(chunks)

    user_input = st.text_area("🙏 Ask your spiritual question:")

    if user_input:
        with st.spinner("🔍 Finding wisdom in the scriptures..."):
            relevant_chunks = find_similar_chunks(user_input, vectorizer, tfidf_matrix, chunks)
            final_prompt = build_prompt(user_input, relevant_chunks, agent_type)
            
            try:
                response = st.session_state.chat_model.generate_content(final_prompt)
                st.markdown("### 🪔 Guru's Wisdom")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")