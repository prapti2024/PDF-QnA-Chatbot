# vectordb.py
import os
import shutil
import tempfile
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from docling.document_converter import DocumentConverter

VECTOR_DIR = "pdf_vector_db"
COLLECTION_NAME = "pdf_collection"

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

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    converter = DocumentConverter()
    result = converter.convert(file_path).document.export_to_text()
    return result

def chunk_and_store_text(db: Chroma, text: str) -> int:
    """Chunk text and store embeddings in Chroma."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks: List[str] = splitter.split_text(text)
    db.add_texts(chunks)  # automatically persisted
    return len(chunks)

def process_pdf(file, fresh: bool = False) -> int:
    """Save uploaded PDF, extract text, chunk, and add to Chroma DB."""
    db = init_db(fresh=fresh)

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text_from_pdf(tmp_path)
        num_chunks = chunk_and_store_text(db, text)
    finally:
        os.remove(tmp_path)

    return num_chunks
