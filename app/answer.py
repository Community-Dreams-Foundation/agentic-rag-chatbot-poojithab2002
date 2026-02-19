from typing import List, Dict


def build_answer(query: str, chunks: List[Dict]) -> Dict:
    """
    Builds a grounded answer strictly from retrieved chunks.
    Returns:
        {
            "answer": str,
            "citations": List[Dict]
        }
    """

    if not chunks:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "citations": []
        }

    # Simple sentence extraction
    relevant_sentences = []
    citations = []

    query_terms = query.lower().split()

    for chunk in chunks:
        text = chunk["text"]
        sentences = text.split(".")

        for sentence in sentences:
            if any(term in sentence.lower() for term in query_terms):
                relevant_sentences.append(sentence.strip())

        citations.append({
            "chunk_id": chunk["chunk_id"],
            "source_path": chunk["source_path"],
            "char_start": chunk["char_start"],
            "char_end": chunk["char_end"]
        })

    if not relevant_sentences:
        answer_text = "Relevant documents were found, but no direct matching sentences were identified."
    else:
        answer_text = " ".join(relevant_sentences)

    return {
        "answer": answer_text.strip(),
        "citations": citations
    }
