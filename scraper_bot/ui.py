import os
import requests
import streamlit as st
from embeddings import EmbeddingStore

txt_file = "scraped_content.txt"
api_url = "http://127.0.0.1:8000"

# Initialize session state if not already set
if "state" not in st.session_state:
    st.session_state.state = "input"
    st.session_state.embedding_store = None

# Reset function
def reset_application():
    if os.path.exists(txt_file):
        os.remove(txt_file)
    st.session_state.embedding_store = None
    st.session_state.state = "input"
    st.rerun()

# UI - Website Input
if st.session_state.state == "input":
    st.title("Web Info Chatbot")
    url = st.text_input("Enter Website URL:", "")
    if st.button("Submit") and url:
        st.session_state.state = "loading"
        st.session_state.url = url
        st.rerun()

# UI - Loading State
if st.session_state.state == "loading":
    st.title("Processing... Please wait.")

    with st.spinner("Scraping website and storing embeddings..."):
        data = {
            "url": st.session_state.url,
            "max_pages": 10
        }

        try:
            response = requests.post(f"{api_url}/api/scrape_web", json=data)
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")

        if response_json.get("success"):
            content = response_json.get("detail")
            with open(txt_file, "w", encoding="utf-8") as file:
                file.write(content)
            
            store = EmbeddingStore()
            store.add_text(content)
            st.session_state.embedding_store = store
            st.session_state.state = "chat"
            st.rerun()
        else:
            st.error(response_json.get("detail", "An unknown error occurred."))
            if st.button("Reset Application"):
                reset_application()

# UI - Chat Interface
if st.session_state.state == "chat":
    st.title("Chat with the Website")
    if st.button("Reset Application"):
        reset_application()
    
    query = st.text_input("Ask something about the website:", "")
    if query and st.button("Submit Query"):
        store = st.session_state.embedding_store
        results = store.search(query, top_k=3)
        st.write("### Answer:") 
        st.write(results[0] if results else "No relevant information found.")