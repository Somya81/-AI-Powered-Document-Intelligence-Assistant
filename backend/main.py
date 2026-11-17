
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from backend.document_processor import extract_text_from_pdf
from backend.rag_engine import create_vector_store, search_documents
from backend.llm_service import generate_answer


app = FastAPI(
    title="Engineering Document Intelligence Assistant",
    description="AI-powered engineering document question answering system",
    version="1.0.0"
)

UPLOAD_DIR = Path("documents")
UPLOAD_DIR.mkdir(exist_ok=True)

document_index = None
document_chunks = []
document_filename = None


@app.get("/")
def home():
    return {
        "message": "Engineering Document Intelligence API is running!"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    global document_index
    global document_chunks
    global document_filename

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / Path(file.filename).name

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = extract_text_from_pdf(str(file_path))

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        index, chunks = create_vector_store(pages)

        if index is None or not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create document index"
            )

        document_index = index
        document_chunks = chunks
        document_filename = file.filename

        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks)
        }

    finally:
        await file.close()


@app.get("/ask")
def ask_question(question: str):

    if document_index is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF first"
        )

    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    results = search_documents(
        question,
        document_index,
        document_chunks,
        top_k=5
    )

    if not results:
        return {
            "question": question,
            "filename": document_filename,
            "answer": "I could not find sufficiently relevant information in this document.",
            "sources": [],
            "retrieved_chunks": 0
        }

    results = sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )

    context_parts = []

    for item in results:
        context_parts.append(
            f"Page {item['page']}:\n{item['text']}"
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question,
        context
    )

    sources = sorted({
        item["page"] for item in results
    })

    return {
        "question": question,
        "filename": document_filename,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": len(results)
    }
