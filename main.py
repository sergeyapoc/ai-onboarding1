import os
from dotenv import load_dotenv
from groq import Groq

# Загружаем ключ из файла .env
load_dotenv()

# Подключаемся к Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Отправляем первый промпт
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "Ты опытный ИИ-инженер. Отвечай кратко и по делу."},
        {"role": "user", "content": "Привет! Объясни простыми словами, что такое промпт-инжиниринг."}
    ],
    model="openai/gpt-oss-120b",
    temperature=0.3
)

# Выводим ответ в консоль
print(response.choices[0].message.content)
