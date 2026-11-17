import os
import glob
import chromadb
from fastembed import TextEmbedding

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "runbooks_collection"
DOCS_DIR = "data/docs"

def build_vector_index():
    print("Инициализация модели эмбеддингов...")
    embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print(f"Подключение к ChromaDB ({CHROMA_PATH})...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Пересоздаём коллекцию при запуске prepare_data.py, чтобы не плодить дубликаты
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

        # Разбиваем документ на абзацы/секции (простой чанкинг)
        chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 30]

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_index": idx})
            ids.append(f"{filename}_{idx}_{doc_counter}")
            doc_counter += 1

    print(f"Генерация векторов для {len(documents)} фрагментов текста...")
    embeddings = [vec.tolist() for vec in embed_model.embed(documents)]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Готово! В векторную базу сохранено {len(documents)} записей.")

if __name__ == "__main__":
    # Здесь же может вызываться твоя функция создания SQLite БД, если она есть в этом файле
    build_vector_index()
