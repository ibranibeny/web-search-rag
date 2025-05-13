
# Web Search RAG

## 📦 Installation

Follow these steps to install and set up the environment:

### 1. Clone the Repository

Download the project files from GitHub:

```bash
git clone https://github.com/ibranibeny/web-search-rag.git
cd web-search-rag
```

### 2. Set Up Python Environment

Ensure you're using **Python 3.8 or higher**. You can optionally create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Use `pip` to install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

> This will install:
> - `duckduckgo-search`: to retrieve web results
> - `openai`: to access language models via API
> - and other supporting libraries

### 4. Set Your Environment Variables

Set your API key for OpenAI before running the app:

```bash
export OPENAI_API_KEY=your_api_key_here   # On Windows: set OPENAI_API_KEY=your_api_key_here
```

### 5. Run the Application

You’re now ready to run the CLI script:

```bash
python main.py
```

---

## 🚀 Usage

After installation, run the CLI application using:

```bash
python main.py
```

You will be prompted to enter a question. The application will:
1. Perform a web search using DuckDuckGo.
2. Retrieve top relevant snippets.
3. Send the question + context to a language model (e.g., GPT-4).
4. Output a concise and context-aware answer.

---

## 🧱 Architecture

```
+-------------+        +----------------+        +-----------------+
|  User Input | -----> | Web Retriever  | -----> |     LLM (GPT)   |
+-------------+        +----------------+        +-----------------+
                                                |
                                        +-------v--------+
                                        | Final Response |
                                        +----------------+
```

- **Web Retriever**: Uses `duckduckgo_search` to fetch contextual snippets.
- **LLM Interface**: Calls GPT or another model with the query and context.
- **CLI Interface**: Prints the answer in the terminal.

---

## 🤖 What is Agentic AI?

**Agentic AI** refers to AI systems that can:
- Autonomously reason about tasks
- Choose appropriate tools or steps
- Chain multiple actions or queries
- Adapt based on intermediate results

Agentic AI makes the system smarter, extensible, and capable of multi-step reasoning.

---
