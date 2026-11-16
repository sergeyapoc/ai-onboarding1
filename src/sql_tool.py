import sqlite3
import json

DB_PATH = "data/security_logs.db"


def get_db_schema() -> str:
    """Возвращает схему таблицы для системного промпта агента."""
    return """
    Table: system_logs
    Columns:
    - id (INTEGER): Primary key
    - timestamp (TEXT): ISO 8601 timestamp (e.g., '2025-05-01T00:49:26+00:00')
    - system_name (TEXT): Hostname (e.g., 'casb-proxy-01', 'casb-proxy-02', 'pam-vault-01', 'vuln-scan-01')
    - component (TEXT): Service component ('CASB', 'PAM', 'Vulnerability_Scanner')
    - log_level (TEXT): Severity ('INFO', 'WARN', 'ERROR')
    - corr_id (TEXT): Correlation UUID
    - user_id (TEXT): Actor ('SUPERUSER', 'ADMIN', 'STANDARDUSER', 'SYSTEM')
    - message (TEXT): Detailed log message
    """


def execute_sql_query(query: str) -> str:
    """Безопасно выполняет SELECT-запрос к базе данных security_logs.db."""
    cleaned_query = query.strip()

    # Защита: разрешаем только чтение данных (SELECT)
    if not cleaned_query.upper().startswith("SELECT"):
        return json.dumps({"error": "Security violation: Only SELECT queries are allowed."})

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Чтобы получать результаты в виде словарей с именами колонок
        cursor = conn.cursor()
        cursor.execute(cleaned_query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not rows:
            return json.dumps({"result": "Query executed successfully, but returned 0 rows."})
        return json.dumps({"result": rows}, ensure_ascii=False)

    except sqlite3.Error as e:
        return json.dumps({"error": f"SQL execution error: {str(e)}"})
