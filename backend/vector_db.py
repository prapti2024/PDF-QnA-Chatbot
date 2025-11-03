# vectordb.py
import os
import shutil
import tempfile
from typing import List
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DIR = "pdf_vector_db"
COLLECTION_NAME = "pdf_collection"

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def init_db(fresh: bool = False) -> Chroma:
    """Initialize Chroma DB. Optionally start fresh."""
    if fresh and os.path.exists(VECTOR_DIR):
        shutil.rmtree(VECTOR_DIR)
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DIR,
        embedding_function=embedding_model
    )

def extract_pages(file_path: str):
    """
    Stream PDF pages one by one using PyMuPDF.
    Returns a generator of (page_number, text)
    """
    with fitz.open(file_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                yield i, text

def chunk_and_store_page(db: Chroma, text: str, page_number: int) -> int:
    """
    Chunk text from a single page and store it in Chroma with metadata.
    Returns number of chunks added.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks: List[str] = splitter.split_text(text)
    db.add_texts(
        texts=chunks,
        metadatas=[{"page": page_number}] * len(chunks)
    )
    return len(chunks)

def process_pdf(file, fresh: bool = False) -> int:
    """
    Save uploaded PDF, process page-by-page, chunk text, and store embeddings in Chroma.
    Returns total number of chunks stored.
    """
    db = init_db(fresh=fresh)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file, tmp)
        tmp_path = tmp.name

    total_chunks = 0
    try:
        for page_number, text in extract_pages(tmp_path):
            chunks = chunk_and_store_page(db, text, page_number)
            total_chunks += chunks
            print(f" Processed page {page_number}: {chunks} chunks")


    finally:
        os.remove(tmp_path)

    print(f"Total chunks stored: {total_chunks}")
    return total_chunks
