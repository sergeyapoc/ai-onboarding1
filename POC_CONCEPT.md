# PoC Concept: AI Security Incident & Log Analyzer (SecOps Copilot)

## 1. Problem Statement & Expected Value
**Problem:** Security Operations (SecOps) and DevOps engineers spend significant time manually querying raw system logs to calculate incident frequencies and cross-referencing findings with scattered internal troubleshooting manuals (Runbooks) and post-mortems. This slows down Mean Time to Resolution (MTTR).
**Expected Value:** An AI-powered conversational assistant that unifies structured log analytics (Text-to-SQL) and unstructured technical documentation search (RAG) into a single real-time interface, reducing incident triage time from minutes to seconds.

## 2. Target User & Usage Scenarios
**Target User:** SecOps Engineer / Site Reliability Engineer (SRE) / L2 Support Specialist.
**Key Scenarios:**
- **Fact-based queries (RAG):** *"What is the standard remediation procedure when the Threat Score enrichment service is unreachable?"*
- **Data-driven queries (Text-to-SQL):** *"How many ERROR-level logs were recorded for the CASB component, and which user IDs triggered them?"*
- **Hybrid analytical queries (SQL + RAG):** *"Identify the most frequent error component in the logs and summarize the root cause and mitigation steps based on our incident runbooks."*

## 3. Architecture & Planned AI Capabilities
- **Orchestrator / Agent:** LLM-based routing agent (`openai/gpt-oss-120b` via Groq API) equipped with function calling (Tools) to dynamically choose between SQL execution, RAG retrieval, or multi-step reasoning.
- **Structured Data Tool (Text-to-SQL):** Converts natural language questions into safe `SELECT` queries executed against a local SQLite database (`security_logs.db`).
- **Unstructured Data Tool (RAG):** Uses `fastembed` (`paraphrase-multilingual-MiniLM-L12-v2`) to retrieve relevant sections from Markdown Runbooks and Post-Mortems.
- **Real-time Execution:** Every user prompt triggers live API inference, dynamic tool invocation, and grounded response generation.

## 4. Data Inputs & Tech Stack
- **Structured Data:** SQLite database populated with security audit logs (`timestamp`, `system_name`, `component`, `log_level`, `corr_id`, `user_id`, `message`).
- **Unstructured Data:** Markdown documents containing remediation runbooks and incident post-mortems (`casb_runbook.md`, `pam_vault_policy.md`, `postmortem_2025_05.md`).
- **Tech Stack:** Python 3.14, Groq SDK, SQLite3, FastEmbed, NumPy.
