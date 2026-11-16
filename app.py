from src.agent import SecOpsAgent

def main():
    agent = SecOpsAgent()
    print("\n=== SecOps AI Copilot запущен! ===")
    print("Примеры вопросов:")
    print("1. [SQL] Сколько всего записей уровня ERROR в логах и какие user_id их вызвали?")
    print("2. [RAG] Какое максимальное время сессии разрешено в PAM и что делать при ошибке MFA?")
    print("3. [HYBRID] Какой компонент чаще всего выдаёт ERROR, в чём была причина сбоя 1 мая и как её чинить по регламенту?")
    print("Введите 'exit' для выхода.\n")

    while True:
        user_input = input("Вы: ").strip()
        if user_input.lower() in ["exit", "quit", "выход"]:
            break
        if not user_input:
            continue

        print("\n[Агент анализирует запрос...]")
        answer = agent.ask(user_input)
        print(f"\nCopilot:\n{answer}\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()
