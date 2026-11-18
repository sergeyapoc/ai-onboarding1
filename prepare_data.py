import os
import glob
import requests
import chromadb

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "runbooks_collection"
DOCS_DIR = "data/docs"
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"

def get_ollama_embeddings(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        OLLAMA_URL,
        json={"model": EMBED_MODEL, "input": texts}
    )
    response.raise_for_status()
    return response.json()["embeddings"]

def build_vector_index():
    print(f"Подключение к ChromaDB ({CHROMA_PATH})...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    md_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
    if not md_files:
        print(f"Внимание: не найдены .md файлы в папке {DOCS_DIR}")
        return

    documents = []
    metadatas = []
    ids = []

    doc_counter = 0
    for file_path in md_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 30]

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_index": idx})
            ids.append(f"{filename}_{idx}_{doc_counter}")
            doc_counter += 1

    print(f"Генерация векторов через Ollama ({EMBED_MODEL}) для {len(documents)} фрагментов...")
    embeddings = get_ollama_embeddings(documents)

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Готово! В векторную базу сохранено {len(documents)} записей.")

if __name__ == "__main__":
    build_vector_index()
