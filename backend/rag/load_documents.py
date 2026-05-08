import fitz 
from pathlib import Path

def load_document(file_path: str) -> str:
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"file path {path} does not exist")
    
    path_suffix = path.suffix
    
    if path_suffix == '.pdf':
        return _load_pdf(path)
    
    elif path_suffix == '.md':
        return _load_markdown(path)
    else:
        raise ValueError("No valid file format")
    
    
def _load_pdf(path: Path) -> str:
    doc = fitz.open(path)
    text = []
    for page in doc:
        page_text = page.get_text()
        text.append(page_text)
    
    doc.close()
    
    text = "\n".join(text)
    
    return text
        

def _load_markdown(path: Path) -> str:
    return path.read_text()
    
if __name__ == "__main__":
    text = load_document("backend/rag/documents/Schaefer_Mehlhorn_2017.md")
    print(f"Loaded {len(text)} characters")
    print(text[:500])  # Erste 500 Zeichen als Sanity Check