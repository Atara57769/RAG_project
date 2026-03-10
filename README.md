# 🔍 RAG Project — AI Agent for Project Documentation

An intelligent RAG (Retrieval-Augmented Generation) system that lets you ask natural language questions about your project's documentation.

The system automatically routes each question to one of two knowledge sources: a vector store (Pinecone) for semantic search, or structured data (JSON) for decisions, rules, warnings, and dependencies.

---

## 🏗️ Architecture

```
User Question
      ↓
  RouterQueryEngine (PydanticSingleSelector)
      ├── decisions / rules / warnings / dependencies  →  structured_data.json  →  LLM  →  Answer
      └── code / architecture / general documentation  →  Pinecone (vectors)    →  LLM  →  Answer
```

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `chat.py` | Gradio chat interface — main entry point |
| `workflow.py` | Event-Driven Workflow using LlamaIndex |
| `events.py` | Event definitions (RouterEvent, RetrieveEvent, etc.) |
| `global_settings.py` | LLM, Embeddings, Pinecone, and Router configuration |
| `load_data.py` | Index documents into Pinecone (run once) |
| `extract_structured_data.py` | Extract structured data from docs into JSON (run once) |
| `structured_data.json` | Structured data: decisions, rules, warnings, dependencies |
| `docs/` | Source documents folder (`.md` files) |
| `rag_workflow.html` | Visual diagram of the Workflow |

---

## ⚙️ Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
llama-index
llama-index-llms-groq
llama-index-embeddings-cohere
llama-index-vector-stores-pinecone
llama-index-program-openai
llama-index-utils-workflow
gradio
pinecone-client
cohere
python-dotenv
urllib3
pydantic
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
COHERE_API_KEY=your_cohere_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

### 3. Add Your Documents

Place your `.md` documentation files inside the `docs/` folder.

### 4. Run One-Time Setup Scripts

These only need to be run once (or when your documents change):

```bash
# Index documents into Pinecone (semantic search)
python load_data.py

# Extract structured data (decisions, rules, warnings, dependencies)
python extract_structured_data.py
```

### 5. Launch the Chat Interface

```bash
python chat.py
```

Open your browser at: http://127.0.0.1:7860

---

## 💬 Example Questions

### Routed to structured_data.json

| Question | What you'll get |
|----------|----------------|
| `What decisions were made in the project?` | List of all architectural and design decisions |
| `What are the project rules?` | Coding and workflow rules |
| `What warnings exist in the project?` | All warnings with severity levels |
| `What dependencies does the project use?` | Full list of dependencies and their purpose |
| `Summarize the project dependencies` | Overview of all libraries and tools used |

### Routed to Pinecone (semantic search)

| Question | What you'll get |
|----------|----------------|
| `How does the API work?` | Context from API-related documentation |
| `How are tasks created?` | Code and logic for task creation |
| `What testing framework is used?` | Testing setup and configuration details |
| `Explain the agent architecture` | Overview from architecture docs |

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq — `llama-3.3-70b-versatile` |
| Embeddings | Cohere — `embed-multilingual-v3.0` |
| Vector Store | Pinecone |
| Orchestration | LlamaIndex Workflows |
| Routing | LlamaIndex `RouterQueryEngine` + `PydanticSingleSelector` |
| UI | Gradio |

---

## 🔄 How the Routing Works

The `PydanticSingleSelector` reads the description of each tool and decides automatically:

- **`list_tool`** — *"Useful for summarization questions about decisions, rules, warnings, and dependencies"*
- **`vector_tool`** — *"Useful for retrieving specific context about code, architecture, and documentation"*

The LLM picks the best tool based on the user's question — no manual logic needed.

---

## 📊 Workflow Visualization

After running `chat.py`, a visual diagram of the full workflow is saved to `rag_workflow.html`. Open it in your browser to see all steps and event connections.