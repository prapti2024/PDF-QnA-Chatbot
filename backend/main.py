# app.py
from fastapi import FastAPI, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from .vector_db import process_pdf
from .llm import answer_query   

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile, fresh: bool = False):
    """
    Upload a PDF, extract text, chunk, and store embeddings.
    """
    num_chunks = process_pdf(file.file, fresh=fresh)
    return {"num_chunks": num_chunks}

@app.post("/ask/")
async def query_pdf(question: str = Form(...)):
    """
    Query the PDF content using semantic search.
    Returns top-k relevant chunks.
    """
    results = answer_query(question)
    return {"query": question, "answer": results}


