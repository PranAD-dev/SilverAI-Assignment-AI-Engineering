# Handbook Generator

An AI-powered chat application that generates 20,000+ word handbooks from uploaded PDF documents using LightRAG knowledge graphs and Grok 4.1.

## Architecture

```
PDF Upload  -->  LightRAG (Knowledge Graph)  -->  Chat UI (Gradio)  -->  Handbook (20k+ words)
 (pdfplumber)     (OpenAI embeddings)              (Grok 4.1)          (AgentWrite pipeline)
```

| Component          | Technology            | Purpose                            |
| ------------------ | --------------------- | ---------------------------------- |
| **Frontend**       | Gradio                | Chat interface + PDF upload        |
| **LLM**            | Grok 4.1 (xAI API)   | RAG answers + handbook generation  |
| **RAG**            | LightRAG              | Knowledge graph from PDFs          |
| **Embeddings**     | OpenAI text-embedding | Vector embeddings for retrieval    |
| **PDF Processing** | pdfplumber            | Text extraction from uploads       |

## Setup

### Prerequisites

- Python 3.10+
- API keys for [xAI (Grok)](https://console.x.ai/) and [OpenAI](https://platform.openai.com/api-keys)

### 1. Clone and install

```bash
git clone https://github.com/PranAD-dev/SilverAI-Assignment-AI-Engineering.git
cd SilverAI-Assignment-AI-Engineering
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```
XAI_API_KEY=your-xai-api-key
OPENAI_API_KEY=your-openai-api-key
```

The Supabase fields in `.env` are optional (the app uses local storage by default).

### 3. Run

```bash
python main.py
```

Open **http://127.0.0.1:7860** in your browser.

## Usage

### Upload PDFs

1. Click **Upload PDFs** in the left panel and select one or more PDF files
2. Click **Index PDFs** -- LightRAG will extract text, generate embeddings, and build a knowledge graph
3. Wait for the status to confirm indexing is complete (takes 2-5 min per paper)

### Chat

Type any question in the message box. The system retrieves relevant context from your indexed PDFs and answers using Grok 4.1.

### Generate a Handbook

Type a message containing "create a handbook", "generate a handbook", or "write a handbook", for example:

> Create a handbook on Retrieval-Augmented Generation

The system will:
1. Plan 30+ sections (table of contents, chapters, case studies, etc.)
2. Write each section sequentially, showing live progress
3. Display the final word count when complete
4. Make the handbook available for download as a `.md` file in the left panel

Handbook generation takes approximately 10-20 minutes for 20,000+ words.

## Project Structure

```
main.py                    # Entry point -- builds UI, wires event handlers, launches app
app/
  config.py                # Loads environment variables
  llm_client.py            # Grok 4.1 client (OpenAI-compatible API)
  pdf_processor.py         # PDF text extraction via pdfplumber
  rag_engine.py            # LightRAG knowledge graph (init, insert, query)
  handbook_generator.py    # AgentWrite pipeline (plan -> write sections)
LongWriter-main/           # Reference implementation (AgentWrite research code)
  agentwrite/              # Original plan + write pipeline
  agentwrite/prompts/      # Original prompt templates
```

## How It Works

The handbook generation uses the **AgentWrite** technique from the [LongWriter paper](Documentation/):

1. **Planning phase** -- Grok breaks the user's request into 30+ paragraph-level subtasks, each with a target word count
2. **Writing phase** -- Grok writes each section sequentially, using the plan and previously written text as context to maintain coherence
3. **RAG context** -- LightRAG retrieves relevant content from uploaded PDFs, which is injected into both the planning and writing prompts

This approach overcomes LLM output length limits by generating the document incrementally rather than in a single pass.
