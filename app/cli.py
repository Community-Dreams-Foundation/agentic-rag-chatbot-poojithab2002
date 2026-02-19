import typer
from app.ingest import ingest_directory
import json
from pathlib import Path
from app.chunking import chunk_text
from app.retrieve import search_chunks
from app.answer import build_answer
from app.memory import memory_gate, write_memory




app = typer.Typer()


@app.command()
def hello():
    print("Agentic RAG Chatbot CLI is working!")


@app.command()
def ingest():
    """
    Reads files from sample_docs/, chunks them,
    and saves chunks to data/chunks.jsonl
    """
    documents = ingest_directory()

    print(f"Found {len(documents)} document(s).")

    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc)
        all_chunks.extend(chunks)

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    output_path = data_dir / "chunks.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"Generated {len(all_chunks)} chunks.")
    print(f"Saved to {output_path}")

@app.command()
def search(query: str):
    """
    Searches indexed chunks using BM25.
    """
    results = search_chunks(query)

    print(f"\nTop {len(results)} results:\n")

    for chunk in results:
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_path']}")
        print(f"Text: {chunk['text'][:200]}")
        print("-" * 40)

@app.command()
def ask(query: str):
    """
    Answers a question using retrieved chunks and attaches citations.
    """
    results = search_chunks(query, top_k=3, min_score=0.5)
    response = build_answer(query, results)

    print("\nAnswer:\n")
    print(response["answer"])

    print("\nCitations:\n")
    for citation in response["citations"]:
        print(citation)

@app.command()
def ask(query: str):
    """
    Answers a question using retrieved chunks and attaches citations.
    Also evaluates memory writing.
    """

    # Memory evaluation
    decision = memory_gate(query)
    write_memory(decision)

    results = search_chunks(query, top_k=3, min_score=0.5)
    response = build_answer(query, results)

    print("\nAnswer:\n")
    print(response["answer"])

    print("\nCitations:\n")
    for citation in response["citations"]:
        print(citation)

@app.command()
def sanity():
    """
    Runs minimal end-to-end flow and generates artifacts/sanity_output.json
    """

    # Ensure chunks exist
    documents = ingest_directory()
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc)
        all_chunks.extend(chunks)

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    chunks_path = data_dir / "chunks.jsonl"
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    #  Run QA example
    test_question = "pdf"
    results = search_chunks(test_question, top_k=3, min_score=0.5)
    response = build_answer(test_question, results)

    qa_entry = {
        "question": test_question,
        "answer": response["answer"],
        "citations": []
    }

    for chunk in results:
        qa_entry["citations"].append({
            "source": chunk["source_path"],
            "locator": chunk["chunk_id"],
            "snippet": chunk["text"][:200]
        })

    # Trigger memory example
    memory_input = "I prefer CLI over web UI"
    decision = memory_gate(memory_input)
    write_memory(decision)

    memory_writes = []
    if decision["should_write"]:
        memory_writes.append({
            "target": decision["target"],
            "summary": decision["summary"]
        })

    # Build final JSON
    output = {
        "implemented_features": ["A", "B"],
        "qa": [qa_entry],
        "demo": {
            "memory_writes": memory_writes
        }
    }

    # Save to artifacts/
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    output_path = artifacts_dir / "sanity_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Sanity run complete.")
    print(f"Output written to {output_path}")



if __name__ == "__main__":
    app()
