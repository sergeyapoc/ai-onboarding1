import numpy as np
from fastembed import TextEmbedding

# Инициализируем легкую модель для создания эмбеддингов (поддерживает русский язык)
# При первом запуске она скачает небольшой файл модели (~120 МБ)
model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Наша мини-база знаний (документы)
documents = [
    "Чтобы вернуть товар, обратитесь в магазин с чеком в течение 14 дней.",
    "Наш офис открыт по будням с 9:00 до 18:00 без перерыва на обед.",
    "Для сброса пароля нажмите кнопку 'Забыли пароль' на экране входа.",
    "Доставка курьером занимает от 1 до 3 рабочих дней."
]

# Запрос пользователя (обратите внимание: ни одно слово не совпадает со строкой про пароль!)
query = "Не получается зайти в личный кабинет, потерял доступ"

# Превращаем документы и запрос в числовые векторы (эмбеддинги)
doc_embeddings = list(model.embed(documents))
query_embedding = list(model.embed([query]))[0]

print(f"Размер одного вектора: {len(query_embedding)} чисел")
print(f"Первые 5 чисел вектора запроса: {query_embedding[:5]}\n")

# Ищем самый близкий по смыслу документ (считаем косинусное сходство)
best_score = -1
best_doc = ""

for doc, doc_emb in zip(documents, doc_embeddings):
    # Скалярное произведение нормализованных векторов показывает близость смысла (от -1 до 1)
    score = np.dot(query_embedding, doc_emb)
    print(f"Сходство {score:.2f} -> {doc}")
    if score > best_score:
        best_score = score
        best_doc = doc

print(f"\nЛучший найденный ответ для RAG:\n{best_doc}")
