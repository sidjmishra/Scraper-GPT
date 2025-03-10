from scraper_bot.embeddings import EmbeddingStore, ask_llama

# Function to read text from file and store embeddings
def process_text_file(file_path):
    """Read formatted scraped content and process embeddings."""
    store = EmbeddingStore()

    with open(file_path, "r", encoding="utf-8") as file:
        raw_text = file.read()

    scraped_texts = [text.strip() for text in raw_text.split("=== Page Content ===") if text.strip()]
    
    store.add_scraped_data(scraped_texts)
    return store

# Example usage
if __name__ == "__main__":
    file_path = "scraped_content.txt"
    embedding_store = process_text_file(file_path)

    query = "Products of Arya.AI?"
    relevant_texts = embedding_store.retrieve_relevant_text(query, top_k=3)
    context = "\n\n".join(relevant_texts)

    answer = ask_llama(query, context)
    print("Llama Answer:\n", answer)