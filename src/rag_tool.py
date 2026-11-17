import chromadb
from fastembed import TextEmbedding

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "runbooks_collection"

class RunbookRAG:
    def __init__(self):
        # Подключаемся к уже созданной на диске векторной базе
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)
        # Модель нужна только для перевода входящего запроса пользователя в вектор
        self.embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def search(self, query: str, top_k: int = 3) -> str:
        # 1. Превращаем вопрос пользователя в вектор
        query_embedding = list(self.embed_model.embed([query]))[0].tolist()

        # 2. Ищем ближайшие векторы в ChromaDB
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

# Функция-обёртка для вызова агентом (оставь сигнатуру такой же, как была у тебя в agent.py)
_rag_instance = None

def search_runbooks(query: str) -> str:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RunbookRAG()
    return _rag_instance.search(query)
