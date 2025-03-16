import os
import json
import requests
from fpdf import FPDF
import streamlit as st
from embeddings import EmbeddingStore, ask_llama

txt_file = "scraped_content.txt"
api_url = "http://127.0.0.1:8000"

st.set_page_config(page_title="Researcher's Chatbot", page_icon="🤖")
st.title("Researcher's Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

# Initialize session state if not already set
if "state" not in st.session_state:
    st.session_state.state = "input"
    st.session_state.embedding_store = None
    st.session_state.history = []

# Reset function
def reset_application():
    if os.path.exists(txt_file):
        os.remove(txt_file)
    st.session_state.embedding_store = None
    st.session_state.state = "input"
    st.session_state.history = []
    st.rerun()

# Function to generate PDF report
def generate_pdf():
    if not st.session_state.history:
        st.warning("No conversation history available.")
        return
    print(st.session_state.history)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("DejaVu", "", "scraper_bot/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "scraper_bot/DejaVuSans-Bold.ttf", uni=True)

    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(200, 10, "User & Application Interaction Report", ln=True, align='C')
    pdf.ln(10)

    for entry in st.session_state.history:
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, f"User Query: {entry['query']}", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, f"Response: {entry['response']}\n", align='L')
        pdf.ln(5)

    pdf.output("interaction_report.pdf")
    with open("interaction_report.pdf", "rb") as file:
        st.download_button("Download Report", file, file_name="interaction_report.pdf", mime="application/pdf")

# UI - Website Input
with st.sidebar:
    st.title("Researcher's Chatbot")
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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Report"):
            generate_pdf()
    with col2:
        if st.button("Reset Application"):
            reset_application()
    
    query = st.text_input(f"Ask something about the website: {st.session_state.url}", "")
    if query and st.button("Submit Query"):
        store = st.session_state.embedding_store
        relevant_texts = store.retrieve_relevant_text(query, top_k=3)
        context = "\n\n".join(relevant_texts)

        answer = ask_llama(query, context)
        
        st.write("### Answer:") 
        response = answer if answer else "No relevant information found."
        st.write(response)

        # Store in history
        st.session_state.history.append({"query": query, "response": response})