# Dynamic AI Chatbot for Engineering Assistance

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![Groq Cloud](https://img.shields.io/badge/Inference-Groq_LPU-F05A24.svg)](https://groq.com/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-green.svg)](https://www.trychroma.com/)
[![Instructor](https://img.shields.io/badge/Schema-Instructor_%2B_Pydantic-orange.svg)](https://github.com/jxnl/instructor)

A high-speed, local-first technical AI agent designed for engineering workflows, hardware design calculations, datasheet analysis, and live documentation retrieval[cite: 1]. Built using **Streamlit**, **Groq Cloud**, **Model Context Protocol (MCP)**, **ChromaDB**, and **Instructor**[cite: 1].

---

## Visual Interface

![AI Engineering Assistant Interface](./Demo_pic.png)

---

## Core Highlights & Key Features

### 1. Model Context Protocol (MCP) Integration
* **Decoupled Architecture:** Runs an isolated FastMCP server over standard input/output (`stdio`) to expose specialized tools to the reasoning engine[cite: 1].
* **AST Safe Math Evaluation:** Evaluates algebraic and arithmetic formulas via Python's Abstract Syntax Tree (`ast`) without relying on hazardous `eval()` calls[cite: 1].
* **Datasheet & Doc Querying:** Directly queries offline vector databases for component ratings, pinouts, and thermal tolerances[cite: 1].
* **DuckDuckGo Web Search:** Fetches real-time web documentation, errata, and pinout diagrams on demand[cite: 1].

### 2. Embedded Vector RAG (ChromaDB)
* **Local Persistence:** Retains document chunks locally under `./chroma_data` using ChromaDB and cosine distance matching[cite: 1].
* **Offline Embeddings:** Employs the lightweight `all-MiniLM-L6-v2` SentenceTransformer model to perform embeddings completely on-device without incurring extra cloud API costs[cite: 1].

### 3. Dual-Layer Security Guardrails
* **Pre-Inference Input Guardrail:** Inspects incoming prompts via regex patterns to intercept jailbreaks, system prompt extractions, and credential theft before reaching the LLM[cite: 1].
* **Post-Inference Output Redaction:** Uses Pydantic field validators to sanitize responses, automatically masking emails (`[REDACTED_EMAIL]`), phone numbers (`[REDACTED_PHONE]`), and preventing accidental leaks of Groq API keys (`gsk_*`)[cite: 1].

### 4. Deterministic Schema Enforcement & Telemetry
* **Instructor + Pydantic:** Guarantees strict JSON schemas containing the final response text, intent classification, confidence scores, and extracted topic tags[cite: 1].
* **Streamlit Telemetry Drawer:** Displays live intent detection, topic categorization, and confidence metrics directly underneath each response bubble in the web interface[cite: 1].

### 5. Dynamic Persona Management
* **Sidebar Controls:** Update the system prompt on the fly to instantly switch behavior from a detailed hardware engineer to an embedded systems tutor[cite: 1].
* **State Persistence:** Preserves conversational memory across Streamlit re-renders using a centralized `ConversationManager`[cite: 1].

---

## Technologies & Stack

* **Frontend UI:** Streamlit[cite: 1]
* **Inference Platform:** Groq Cloud (`openai/gpt-oss-20b` / `llama-3.3-70b-versatile`)[cite: 1]
* **Tool Interoperability:** Model Context Protocol (`mcp`) via `stdio`[cite: 1]
* **Structured Output:** Instructor & Pydantic[cite: 1]
* **Vector Store & Embeddings:** ChromaDB & Sentence-Transformers (`all-MiniLM-L6-v2`)[cite: 1]
* **Live Web Retrieval:** DuckDuckGo Search (`ddgs`)[cite: 1]

---

## System Architecture & Workflow

```
                           +-------------------------------+
                           |    Streamlit Web Interface    |
                           +---------------+---------------+
                                           |
                                   (Prompt Submitted)
                                           v
                           +-------------------------------+
                           |      Input Guardrail Trap     |  ---> [Blocks Injection / Jailbreak]
                           |       (guardrails.py)         |
                           +---------------+---------------+
                                           | (Validated String)
                                           v
                           +-------------------------------+
                           |      ConversationManager      |
                           +---------------+---------------+
                                           |
          +--------------------------------+--------------------------------+
          |                                                                 |
   (Phase 1: Tool Call)                                            (Phase 2: Final Synthesis)
          v                                                                 v
+--------------------+                                            +--------------------+
|  MCP Client Bridge |                                            |  Instructor Client |
|   (mcp_client.py)  |                                            |    (Groq Cloud)    |
+---------+----------+                                            +---------+----------+
          | (stdio)                                                                 |
          v                                                                         v
+--------------------+                                            +--------------------+
|     MCP Server     |                                            |   ChatbotResponse  |
|   (mcp_server.py)  |                                            |  (schemas.py PII   |
+---------+----------+                                            |   Output Filter)   |
          |                                                               +---------+----------+
          +--> [evaluate_math_expression] (AST Math)                                |
          +--> [query_knowledge_base] (ChromaDB Vector RAG)                         v
          +--> [web_search] (DuckDuckGo Live Web Search)                  +--------------------+
                                                                          | Streamlit Response |
                                                                          |    + Telemetry     |
                                                                          +--------------------+
```

---

## Project Structure

```plaintext
.
├── app.py                  # Streamlit web interface with telemetry badges & sidebar controls
├── ConversationManager.py  # Central orchestrator: handles tool discovery, execution & schema synthesis
├── mcp_client.py           # Async stdio bridge connecting conversation loops to MCP servers
├── mcp_server.py           # Tool server providing AST math, vector queries, and web searches
├── rag_pipeline.py         # ChromaDB client management, cosine vector lookups, and embedding pipeline
├── schemas.py              # Pydantic schema validation, confidence tracking, and PII output guardrails
├── guardrails.py           # Pre-inference prompt injection and secret theft filters
├── seed_rag.py             # Script to pre-populate local ChromaDB vector store with engineering docs
├── test_guardrails.py      # Unit test script validating input/output security guardrails
├── test_validation.py      # Verification script ensuring Instructor schema outputs
├── requirements.txt        # Full project dependencies
└── Demo_pic.png            # Interface demo image asset
```

---

## Getting Started

### 1. Prerequisites
* **Python 3.10+**[cite: 1]
* A **Groq API Key** (Obtain from the [Groq Console](https://console.groq.com/))[cite: 1]

### 2. Clone and Prepare Environment
```bash
git clone [https://github.com/Hammad06Irfan/dynamic-ai-chatbot.git](https://github.com/Hammad06Irfan/dynamic-ai-chatbot.git)
cd dynamic-ai-chatbot
```

Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Export your Groq API key to your environment variables[cite: 1]:

*On macOS / Linux:*
```bash
export GROQ_API_KEY="gsk_your_actual_api_key_here"
```

*On Windows (Command Prompt):*
```cmd
setx GROQ_API_KEY "gsk_your_actual_api_key_here"
```

### 4. Seed the Vector Store
Populate the local ChromaDB database with default hardware datasheets and pinout documentation[cite: 1]:
```bash
python seed_rag.py
```

### 5. Run the Application
Launch the Streamlit interface[cite: 1]:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser to start using the assistant[cite: 1].

---

## Verification & Testing

Verify that your schema validation and security guardrails function as intended[cite: 1]:

* **Test Guardrails (Input Injections & Output Redaction):**
  ```bash
  python test_guardrails.py
  ```
  Expected output confirms blocked injection attempts and masked email/phone patterns[cite: 1].

* **Test Pydantic Schema Extraction:**
  ```bash
  python test_validation.py
  ```
  Expected output displays parsed intent categories, confidence scores, and extracted topic keywords[cite: 1].
