# backend/rag/ingest.py

from pathlib import Path
from backend.rag.load_documents import load_documents
from backend.rag.chunking import chunk_text
from backend.rag.embed import embed_text
from backend.db.database import SessionLocal
from backend.db.models import Chunks
from backend.db.repository import replace_chunks

def parse_source_author(stem: str) -> tuple[str, str]:
    source = stem
    author = stem.rsplit("_", 1)[0]
    author = author.replace("_", " & ")
    return (source, author)

def ingest_documents(documents_dir: str):
    doc_path = Path(documents_dir)
    all_chunks: list[Chunks] = []

    for file in doc_path.iterdir():
        if file.suffix not in ['.pdf', '.md']:
            continue
        print(f"Processing {file.name}...")
        source, author = parse_source_author(file.stem)   # file.stem = Name ohne Endung
        text = load_documents(str(file))
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):                 # i -> chunk_index
            embedding = embed_text(chunk)
            all_chunks.append(Chunks(
                source=source,
                author=author,
                chunk_index=i,
                text=chunk,
                embedding=embedding,                       # pgvector nimmt die Liste direkt
            ))
        print(f"File: {file.name} -> {len(chunks)} chunks")

    with SessionLocal() as db:                             # Script: Session als Context-Manager
        replace_chunks(db, all_chunks)
    print(f"Stored {len(all_chunks)} chunks.")
        
if __name__ == "__main__":
    ingest_documents("backend/rag/documents")