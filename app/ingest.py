from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader


def read_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    text = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text.append(extracted)
    return "\n".join(text)


def ingest_directory(directory: str = "sample_docs") -> List[Dict]:
    """
    Reads all supported files in a directory and returns a list of documents.
    Each document is a dict with:
        - doc_id
        - source_path
        - text
    """
    base_path = Path(directory)

    if not base_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' not found.")

    documents = []
    doc_counter = 0

    for file_path in base_path.glob("*"):
        if file_path.suffix.lower() not in [".txt", ".md", ".pdf"]:
            continue

        doc_id = f"doc_{doc_counter}"

        if file_path.suffix.lower() in [".txt", ".md"]:
            text = read_txt(file_path)
        elif file_path.suffix.lower() == ".pdf":
            text = read_pdf(file_path)
        else:
            continue

        documents.append({
            "doc_id": doc_id,
            "source_path": str(file_path),
            "text": text
        })

        doc_counter += 1

    return documents
