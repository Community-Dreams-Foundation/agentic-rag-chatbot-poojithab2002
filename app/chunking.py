from typing import List, Dict


def chunk_text(doc: Dict, chunk_size: int = 800, overlap: int = 150) -> List[Dict]:
    """
    Splits a document into overlapping character-based chunks.
    """

    text = doc["text"]
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk_content = text[start:end]

        chunks.append({
            "chunk_id": f"{doc['doc_id']}_{chunk_index}",
            "doc_id": doc["doc_id"],
            "source_path": doc["source_path"],
            "char_start": start,
            "char_end": end,
            "text": chunk_content
        })

        start += chunk_size - overlap
        chunk_index += 1

    return chunks
