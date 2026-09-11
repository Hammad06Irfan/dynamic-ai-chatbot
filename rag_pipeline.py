import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

# Local persistence directory
CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "engineering_docs"

# Lightweight local embedding model (runs completely offline on CPU/GPU)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_chroma_collection():
    """Initializes or retrieves persistent ChromaDB collection."""
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

def ingest_document_chunks(docs: List[Dict[str, Any]]):
    """
    Ingests text chunks into the vector store.
    
    docs format: [
        {"id": "doc_1", "text": "...", "metadata": {"source": "datasheet.pdf", "page": 1}},
        ...
    ]
    """
    collection = get_chroma_collection()
    ids = [d["id"] for d in docs]
    documents = [d["text"] for d in docs]
    metadatas = [d.get("metadata", {}) for d in docs]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print(f"[RAG] Successfully ingested {len(docs)} chunks into ChromaDB.")

def query_vector_store(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves top_k most semantically relevant text chunks for a query."""
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k
    )

    extracted_chunks = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, distances):
            extracted_chunks.append({
                "content": doc,
                "source": meta.get("source", "unknown"),
                "similarity_score": round(1.0 - dist, 4)
            })

    return extracted_chunks