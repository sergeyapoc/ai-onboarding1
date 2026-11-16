import os
import json
from dotenv import load_dotenv
from groq import Groq
from src.sql_tool import get_db_schema, execute_sql_query
from src.rag_tool import RunbookRAG

load_dotenv()


class SecOpsAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"
        print("[System] Инициализация RAG-индекса документации...")
        self.rag = RunbookRAG()

        self.system_prompt = f"""You are a Senior SecOps AI Copilot. 
Your job is to investigate security incidents using two tools:
1. `query_security_logs`: Run read-only SQLite SELECT queries against the logs database.
2. `search_runbooks`: Search internal Markdown runbooks, policies, and post-mortems for troubleshooting steps and root causes.

Database Schema:
{get_db_schema()}

Guidelines:
- Always ground your answers strictly in the data returned by your tools.
- For complex questions, call multiple tools sequentially (e.g., query SQL first to find the top error, then search runbooks for remediation steps).
- Cite the source runbook filenames when providing policy or remediation advice.
- Respond in Russian clearly and concisely.
"""

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_security_logs",
                    "description": "Execute a SQLite SELECT query to analyze structured system logs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Valid SQLite SELECT query (e.g., SELECT component, COUNT(*) FROM system_logs WHERE log_level='ERROR' GROUP BY component)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_runbooks",
                    "description": "Semantic search across security runbooks, policies, and incident post-mortems.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query describing the error, policy, or component to look up."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def ask(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Цикл рассуждений (Reasoning Loop): разрешаем агенту делать до 5 шагов (вызовов инструментов)
        max_iterations = 5
        for step in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.1  # Низкая температура для высокой точности SQL и фактов
            )

            msg = response.choices[0].message

            # Если модель не вызывает инструменты — значит финальный ответ готов
            if not msg.tool_calls:
                return msg.content

            messages.append(msg)

            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if func_name == "query_security_logs":
                    print(f"  [SQL Tool] Выполняю запрос: {args.get('query')}")
                    result = execute_sql_query(args.get("query", ""))
                elif func_name == "search_runbooks":
                    print(f"  [RAG Tool] Ищу в документации: '{args.get('query')}'")
                    result = self.rag.search(args.get("query", ""))
                else:
                    result = json.dumps({"error": "Unknown tool"})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })

        return "Превышен лимит шагов рассуждения агента."
