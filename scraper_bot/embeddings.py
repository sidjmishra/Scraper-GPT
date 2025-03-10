import ollama
import faiss
import numpy as np

class EmbeddingStore:
    def __init__(self, dimension=4096):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # FAISS index for similarity search
        self.text_data = []

    def embed_text(self, text):
        """Generate embeddings using Ollama Mistral."""
        response = ollama.embeddings(model="mistral", prompt=text)
        return np.array(response["embedding"], dtype=np.float32).reshape(1, -1)

    def add_text(self, text):
        """Embed and store text in FAISS."""
        embedding = self.embed_text(text)
        self.index.add(embedding)
        self.text_data.append(text)

    def search(self, query, top_k=3):
        """Retrieve most relevant text based on query."""
        query_embedding = self.embed_text(query)
        _, indices = self.index.search(query_embedding, top_k)
        return [self.text_data[i] for i in indices[0] if i < len(self.text_data)]

# # Read text from file and store embeddings
# def process_text_file(file_path):
#     store = EmbeddingStore()
    
#     with open(file_path, "r", encoding="utf-8") as file:
#         text = file.read()

#     store.add_text(text)
#     return store

# if __name__ == "__main__":
#     file_path = "scraped_content.txt"
#     embedding_store = process_text_file(file_path)

#     query = "What is the Eiffel Tower?"
#     results = embedding_store.search(query, top_k=2)
#     print("Search Results:", results)
