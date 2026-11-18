import requests
import chromadb

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "runbooks_collection"
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"

class RunbookRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

    def _get_query_embedding(self, text: str) -> list[float]:
        response = requests.post(
            OLLAMA_URL,
            json={"model": EMBED_MODEL, "input": [text]}
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]

    def search(self, query: str, top_k: int = 3) -> str:
        query_embedding = self._get_query_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return "Релевантной информации в документации не найдено."

        formatted_results = []
        for doc, meta in zip(documents, metadatas):
            source = meta.get("source", "unknown")
            formatted_results.append(f"[Источник: {source}]\n{doc}")

        return "\n\n---\n\n".join(formatted_results)

_rag_instance = None

def search_runbooks(query: str) -> str:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RunbookRAG()
    return _rag_instance.search(query)
