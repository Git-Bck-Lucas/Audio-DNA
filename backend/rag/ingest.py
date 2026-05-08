# backend/rag/ingest.py

from load_documents import load_document
from chunking import chunk_text
from embed import embed_text
from pathlib import Path

def ingest_documents(documents_dir: str):
    """Load, chunk and embed all documents."""
    doc_path = Path(documents_dir)
    
    for file in doc_path.iterdir():
        if file.suffix not in ['.pdf', '.md']:
            continue
        
        print(f"Processing {file.name}...")
        
        text = load_document(str(file))
        chunks = chunk_text(text)
        embeddings = []
        for chunk in chunks:
            embedding = embed_text(chunk)
            embeddings.append(embedding)

        print(f"File: {file.name}")
        print(f"Chunks: {len(chunks)}")
        print(f"Dimensions: {len(embeddings[0])}")
        
if __name__ == "__main__":
    ingest_documents("backend/rag/documents")