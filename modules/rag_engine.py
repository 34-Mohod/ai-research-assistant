from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def build_vector_store(text):

    chunks = chunk_text(text)
    embeddings = embed_model.encode(chunks)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index, chunks

def ask_question(query, index, chunks):

    q_embedding = embed_model.encode([query])
    _, indices = index.search(np.array(q_embedding), 3)

    context = "\n\n".join([chunks[i] for i in indices[0]])

    prompt = f"""
Answer based only on context.

Context:
{context}

Question:
{query}
"""

    response = ollama.chat(
        model='llama3:latest',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return response['message']['content']