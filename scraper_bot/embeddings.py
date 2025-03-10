import ollama
import faiss
import numpy as np

class EmbeddingStore:
    def __init__(self):
        """Initialize FAISS index and metadata storage."""
        self.index = None
        self.metadata = []

    def embed_text(self, text):
        """Generate embeddings using Ollama Mistral."""
        response = ollama.embeddings(model="llama3", prompt=text)
        embedding = np.array(response["embedding"], dtype=np.float32).reshape(1, -1)

        # Initialize FAISS index with correct dimensions
        if self.index is None:
            self.index = faiss.IndexFlatL2(embedding.shape[1])

        return embedding

    def add_scraped_data(self, scraped_texts):
        """Embed and store structured scraped data from plain text format."""
        for text in scraped_texts:
            embedding = self.embed_text(text)

            # Add to FAISS index
            self.index.add(embedding)
            self.metadata.append({"text": text})

    def search(self, query, top_k=3):
        """Retrieve most relevant text based on query."""
        if self.index is None or self.index.ntotal == 0:
            return "No data available for search."

        query_embedding = self.embed_text(query)
        _, indices = self.index.search(query_embedding, top_k)

        # Return matching metadata
        return [self.metadata[i]["text"] for i in indices[0] if i < len(self.metadata)]

    def retrieve_relevant_text(self, query, top_k=3):
        """Retrieve most relevant text based on query."""
        if self.index is None or self.index.ntotal == 0:
            return ["No relevant data found."]

        query_embedding = self.embed_text(query)
        _, indices = self.index.search(query_embedding, top_k)

        # Return matching metadata
        return [self.metadata[i]["text"] for i in indices[0] if i < len(self.metadata)]
    
def ask_llama(query, context_text):
    """Generate a summarized response using Ollama's Llama model."""
    prompt = (
        f"Use the following context to answer the question concisely:\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Function to read text from file and store embeddings
# def process_text_file(file_path):
#     """Read formatted scraped content and process embeddings."""
#     store = EmbeddingStore()

#     with open(file_path, "r", encoding="utf-8") as file:
#         raw_text = file.read()

#     # Split text based on separators (each `=` line marks a new entry)
#     scraped_texts = [text.strip() for text in raw_text.split("=== Page Content ===") if text.strip()]
    
#     store.add_scraped_data(scraped_texts)
#     return store

# Example usage
# if __name__ == "__main__":
#     file_path = "scraped_content.txt"
#     embedding_store = process_text_file(file_path)

#     query = "Products of Arya.AI?"
#     relevant_texts = embedding_store.retrieve_relevant_text(query, top_k=3)
#     context = "\n\n".join(relevant_texts)

#     answer = ask_llama(query, context)
#     print("Llama Answer:\n", answer)
