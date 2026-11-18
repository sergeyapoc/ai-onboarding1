# Security Incident & Runbook Copilot (AI PoC)

An AI-powered incident investigation assistant designed for Security Operations and DevOps engineers. The agent combines structured SQL querying over system logs with semantic Retrieval-Augmented Generation (RAG) over internal runbooks and postmortems.

## Key Features
* **Hybrid Tool-Calling Agent:** Automatically decides whether to query structured logs (`SQLite`), search documentation (`ChromaDB`), or combine both in a multi-step reasoning loop.
* **Persistent Vector Store:** Uses **ChromaDB** (`data/chroma_db`) for fast semantic retrieval without recomputing embeddings at startup.
* **Local Privacy-First Embeddings:** Generates 768-dimensional vector embeddings locally via **Ollama** (`nomic-embed-text`).
* **SQL Log Analytics:** Executes read-only SQL queries against `security_logs.db` to identify error spikes, affected components, and incident timelines.

## Architecture
1. **Offline Data Preparation (`prepare_data.py`):**
   * Initializes the SQLite database (`data/security_logs.db`) with synthetic security/system logs.
   * Chunks Markdown runbooks (`data/docs/*.md`), generates embeddings via local Ollama API, and persists them into ChromaDB (`data/chroma_db`).
2. **Runtime Agent (`app.py` & `src/agent.py`):**
   * **SQL Tool (`src/sql_tool.py`):** Converts natural language questions into SQLite queries.
   * **RAG Tool (`src/rag_tool.py`):** Embeds user queries via Ollama and retrieves top relevant runbook sections from ChromaDB.

## Prerequisites
* **Python 3.10+**
* **Ollama** installed and running locally ([ollama.com](https://ollama.com))
* **LLM API Key** (configured in `.env`, e.g., `GROQ_API_KEY`)

## Setup & Run Instructions

1. **Clone the repository and create a virtual environment:**
   ```bash
   git clone <your-repo-url>
   cd ai-onboarding
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull the local embedding model in Ollama:**
   Ensure the Ollama background service is running, then download `nomic-embed-text`:
   ```bash
   ollama pull nomic-embed-text
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root (based on `.env.example`) and add your API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

5. **Prepare databases and build the vector index:**
   Run the ingestion script once to generate `security_logs.db` and populate `data/chroma_db`:
   ```bash
   python prepare_data.py
   ```

6. **Start the Copilot application:**
   ```bash
   python app.py
   ```

## Example Queries to Try
* *"Which component generates the most errors, and how do we fix it?"* (Triggers both SQL log aggregation and RAG runbook lookup)
* *"What are the remediation steps for CASB fallback policy issues?"* (Triggers RAG search over `casb_runbook.md`)
* *"Summarize the root cause from the May 2025 postmortem."* (Triggers RAG search over `postmortem_may2025.md`)
