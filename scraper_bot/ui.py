import os
import json
import requests
import streamlit as st
from embeddings import EmbeddingStore, ask_llama

txt_file = "scraped_content.txt"
api_url = "http://127.0.0.1:8000"

st.set_page_config(page_title="Web Info Chatbot", page_icon="🤖")
st.title("Web Info Chatbot")

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
    url = st.text_input("Enter Website URL:", "")
    if st.button("Submit") and url:
        st.session_state.state = "loading"
        st.session_state.url = url
        st.rerun()

# UI - Loading State
if st.session_state.state == "loading":
    st.title("Processing... Please wait.")

    with st.spinner("Scraping website and storing embeddings..."):
        data = {"url": st.session_state.url, "max_pages": 10}

        try:
            response = requests.post(f"{api_url}/api/scrape_web", json=data)
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            st.session_state.state = "input"
            st.rerun()

        if response_json.get("success"):
            content = response_json.get("detail")
            with open(txt_file, "w", encoding="utf-8") as file:
                file.write(content)
            
            scraped_texts = [text.strip() for text in content.split("=== Page Content ===") if text.strip()]
            store = EmbeddingStore()
            store.add_scraped_data(scraped_texts)
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
    
    query = st.text_input(f"Ask something about the website: {st.session_state.url}", "")
    if query and st.button("Submit Query"):
        store = st.session_state.embedding_store
        relevant_texts = store.retrieve_relevant_text(query, top_k=3)
        context = "\n\n".join(relevant_texts)

        answer = ask_llama(query, context)
        st.write("### Answer:") 
        if answer:
            st.write(answer)
        else:
            st.write("No relevant information found.")