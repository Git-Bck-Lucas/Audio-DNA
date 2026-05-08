from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    embeddings = model.encode(text)
    embeddings = embeddings.tolist()
    return embeddings