# Architecture Overview

## Goal
Provide a brief, readable overview of how your chatbot works:
- ingestion
- indexing
- retrieval + grounding with citations
- memory writing
- optional safe tool execution

Keep this short (1–2 pages).

Brief:

This project implements a minimal, reproducible Agentic RAG chatbot that supports:

- File-grounded Q&A with citations (Feature A)
- Selective persistent memory written to markdown (Feature B)
- A universal judge command `make sanity` that generates `artifacts/sanity_output.json`

The system is CLI-based and designed for deterministic, reproducible evaluation.

---

## High-Level Flow

### 1) Ingestion (Upload → Parse → Chunk)
- Supported inputs: .txt, .md, .pdf

- Parsing approach:

  ​	Text and Markdown files are read directly.

  ​	PDFs are parsed using `pypdf` and text is extracted page by page.

- Chunking strategy:

  ​	Fixed-size character chunking (800 characters per chunk).

  ​	Each chunk retains its original character offsets.

  ​	This keeps the system simple and deterministic.

- Metadata captured per chunk (recommended):
  - chunk_id
  - doc_id
  - source_path
  - char_start
  - char_end
  - text
  - Chunks are stored in `data/chunks.jsonl`.

### 2) Indexing / Storage
- Vector store choice (FAISS/Chroma/pgvector/etc):

  ​	No embedding model is used.

  ​	Retrieval is implemented using lexical BM25 via `rank-bm25`.

- Persistence:

  ​	Chunks are stored on disk in `data/chunks.jsonl`.

  ​	The BM25 index is built at query time from stored chunks.

- This keeps the system lightweight and reproducible without external APIs.

### 3) Retrieval + Grounded Answering
- Retrieval method (top-k, filters, reranking):

  ​	BM25 ranking over all chunk texts.

  ​	Top-k (k=3) chunks are selected.

  ​	A minimum score threshold filters irrelevant results.

- Answer construction:
  
  ​	Only retrieved chunks are used.
  
  ​	The answer is composed by selecting relevant sentences from retrieved chunks.
  
  ​	No external knowledge is injected.
  
- How citations are built:
  
  - citation includes: source, locator (page/section), snippet
  
  - `source` (file path)
  
    `locator` (chunk_id)
  
    `snippet` (text excerpt)
  
- Failure behavior:
  - If no chunk passes the score threshold, the system returns:
  
    `I could not find relevant information in the uploaded documents.`
  
    No hallucinated answers are generated.
  
    No fake citations are created.

### 4) Memory System (Selective)
- The system implements selective memory writing.

- What counts as “high-signal” memory:

  ​	User preferences (for example: prefers CLI over web UI)

  ​	Stable professional facts

  ​	Reusable project-level learnings

- What you explicitly do NOT store (PII/secrets/raw transcript):

  ​	Raw transcripts

  ​	Sensitive data

  ​	Secrets

  ​	Temporary conversational context

- How you decide when to write:

  ​	Internally, a decision object is created:

  ```
  {
    	should_write: bool,
    	target: "USER" | "COMPANY",
    	summary: string,
    	confidence: float
  }
  ```

  Memory is written only when `should_write` is true.

- Format written to:
  
  - `USER_MEMORY.md`
  - `COMPANY_MEMORY.md`

### 5) Optional: Safe Tooling (Open-Meteo)
- Not implemented in this baseline submission.

---

## Tradeoffs & Next Steps
- Why this design?

  ​	No external LLM dependency

  ​	No external embedding APIs

  ​	Fully local and reproducible

  ​	Deterministic evaluation for judges

  ​	Minimal moving parts

- What you would improve with more time:

  ​	Hybrid retrieval (BM25 + embeddings)

  ​	Smarter semantic chunking

  ​	Sentence-level citation alignment

  ​	Confidence scoring calibration

  ​	Prompt-injection detection layer

  ​	Streaming responses

  ​	Optional safe sandbox tool execution