import json
from pathlib import Path
from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi


def load_chunks(path: str = "data/chunks.jsonl") -> List[Dict]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError("Chunks file not found. Run ingest first (python -m app.cli ingest).")

    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def tokenize(text: str) -> List[str]:
    return text.lower().split()


def search_chunks(query: str, top_k: int = 3, min_score: float = 0.5) -> List[Dict]:
    """
    Returns top_k chunks whose BM25 score >= min_score.
    If nothing meets the threshold, returns [].
    """
    chunks = load_chunks()
    if not chunks:
        return []

    corpus = [tokenize(chunk.get("text", "")) for chunk in chunks]
    bm25 = BM25Okapi(corpus)

    tokenized_query = tokenize(query)
    if not tokenized_query:
        return []

    scores = bm25.get_scores(tokenized_query)

    scored: List[Tuple[Dict, float]] = list(zip(chunks, scores))
    scored.sort(key=lambda x: x[1], reverse=True)

    filtered = [(c, s) for (c, s) in scored if s >= min_score]
    top = filtered[:top_k]

    # Attach score into each returned chunk (useful for debugging)
    results = []
    for c, s in top:
        c2 = dict(c)
        c2["_score"] = float(s)
        results.append(c2)

    return results
