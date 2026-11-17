# AI-Powered Document Intelligence Assistant

An AI-powered PDF question-answering application that allows users to upload PDF documents and ask questions using natural language.

## Features
- Upload and process PDF documents
- Extract text from PDF pages
- Split text into overlapping chunks
- Generate semantic embeddings using Sentence Transformers
- Retrieve relevant information using FAISS
- Generate answers using OpenRouter LLM
- Display source page numbers

## Tech Stack
- Python
- FastAPI
- Streamlit
- Sentence Transformers
- FAISS
- OpenRouter API
- PyPDF

## Project Structure
```text
backend/
frontend/
requirements.txt
.gitignore
```

## Run Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file in the project root.
3. Add your OpenRouter API key:
`OPENROUTER_API_KEY=your_api_key`
`OPENROUTER_MODEL=openrouter/free`
4. Start backend: `uvicorn backend.main:app --reload`
5. Start frontend: `streamlit run frontend/app.py`

## Note
This project uses an OpenRouter API key. Keep your API key private and never upload your `.env` file.
