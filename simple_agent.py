import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


# 1. Описываем реальные Python-функции (инструменты агента)
def check_order_status(order_id: str) -> str:
    """Проверяет статус заказа по его номеру."""
    fake_db = {
        "101": "Заказ #101 передан курьеру. Ожидаемое время доставки: сегодня до 18:00.",
        "102": "Заказ #102 ожидает оплаты.",
        "103": "Заказ #103 успешно доставлен вчера."
    }
    return fake_db.get(order_id, f"Заказ #{order_id} не найден в базе.")


def calculate_discount(price: float, discount_percent: float) -> str:
    """Вычисляет итоговую цену товара со скидкой."""
    final_price = price * (1 - discount_percent / 100)
    return f"Итоговая цена с учетом скидки {discount_percent}%: {final_price:.2f} руб."


# 2. Создаем инструкцию для нейросети, какие инструменты у неё есть
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Получить статус доставки заказа по его номеру (ID)",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Номер заказа, например '101'"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_discount",
            "description": "Посчитать цену товара после применения скидки в процентах",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "Исходная цена товара"},
                    "discount_percent": {"type": "number", "description": "Размер скидки в процентах"}
                },
                "required": ["price", "discount_percent"]
            }
        }
    }
]


# 3. Запускаем цикл работы агента (Reasoning Loop)
def run_agent(user_prompt: str):
    print(f"Пользователь: {user_prompt}\n")
    messages = [
        {"role": "system",
         "content": "Ты полезный ассистент магазина. Используй доступные инструменты, чтобы отвечать на вопросы."},
        {"role": "user", "content": user_prompt}
    ]

    # Первый шаг: модель думает, нужен ли ей инструмент
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message

    # Если модель решила вызвать инструмент:
    if response_message.tool_calls:
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            print(f"[Агент решил вызвать инструмент]: {func_name} с параметрами {func_args}")

            # Выполняем нужную Python-функцию
            if func_name == "check_order_status":
                tool_result = check_order_status(**func_args)
            elif func_name == "calculate_discount":
                tool_result = calculate_discount(**func_args)
            else:
                tool_result = "Инструмент не найден"

            print(f"[Результат инструмента]: {tool_result}\n")

            # Возвращаем результат работы функции обратно модели
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": tool_result
            })

        # Второй шаг: модель формулирует финальный ответ пользователю с учетом полученных данных
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        print(f"Агент: {final_response.choices[0].message.content}")
    else:
        print(f"Агент: {response_message.content}")


# Тестируем агента!
run_agent("Привет! Подскажи, где сейчас мой заказ 101? И сколько будет стоить ноутбук за 85000 со скидкой 15%?")
