import os
import glob
import json
import numpy as np
from fastembed import TextEmbedding

DOCS_DIR = "data/docs"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class RunbookRAG:
    def __init__(self):
        self.model = TextEmbedding(model_name=EMBEDDING_MODEL)
        self.chunks = []
        self.embeddings = []
        self._index_documents()

    def _index_documents(self):
        """Загружает Markdown-документы, режет на абзацы и строит векторный индекс."""
        md_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
        raw_texts = []

        for filepath in md_files:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Разбиваем документ на смысловые секции по двойному переносу строки (абзацам)
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 20]
            for p in paragraphs:
                self.chunks.append({"source": filename, "text": p})
                raw_texts.append(p)

        if raw_texts:
            self.embeddings = list(self.model.embed(raw_texts))

    def search(self, query: str, top_k: int = 3) -> str:
        """Ищет наиболее релевантные фрагменты регламентов по смыслу."""
        if not self.chunks:
            return json.dumps({"error": "No documentation indexed."})

        query_emb = list(self.model.embed([query]))[0]
        scored_chunks = []

        for chunk, doc_emb in zip(self.chunks, self.embeddings):
            score = float(np.dot(query_emb, doc_emb))
            scored_chunks.append({
                "source": chunk["source"],
                "relevance_score": round(score, 3),
                "content": chunk["text"]
            })

        # Сортируем по убыванию схожести и берем top_k
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_results = scored_chunks[:top_k]

        return json.dumps({"retrieved_docs": top_results}, ensure_ascii=False)
