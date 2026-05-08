from load_documents import load_document

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: The full document text
        chunk_size: Max characters per chunk
        overlap: Characters to repeat between chunks
    """
    # TODO: Split text into sentences first
    # Hint: text.split(". ") is simple but works for papers
    sentences = text.split(". ")
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    # TODO: Build chunks by adding sentences until chunk_size is reached
    for sentence in sentences:
        if current_length + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(sentence)
        else:
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s) > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_length += len(s)
                
            chunks.append(". ".join(current_chunk))
            current_chunk = overlap_sentences
            current_length = overlap_length
            current_chunk.append(sentence)
            current_length += len(sentence)
    
    if current_chunk:
        chunks.append(". ".join(current_chunk))
    
    return chunks

if __name__ == "__main__":
    text = load_document("backend/rag/documents/Schaefer_Mehlhorn_2017.md")
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks[:3]):
       for i in range(min(3, len(chunks) - 1)):
        print(f"--- Ende Chunk {i} ---")
        print(chunks[i][-150:])
        print(f"--- Anfang Chunk {i+1} ---")
        print(chunks[i+1][:150])
        print()