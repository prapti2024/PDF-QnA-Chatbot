import sys
import traceback
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Initialize Bugsink / Sentry first

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="http://233424f4817e4a4398ef81efb49279a7@localhost:8001/1",  # your Bugsink DSN
    integrations=[FastApiIntegration()],
    send_default_pii=True,
    max_request_body_size="always",
    traces_sample_rate=1.0,
)


# Global exception hook


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    sentry_sdk.capture_exception(exc_value)
    print("Uncaught exception captured by Bugsink:")
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

sys.excepthook = handle_exception


# Safe import function

def safe_import(name):
    try:
        return __import__(name, fromlist=["*"])
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Error importing {name}:")
        print(traceback.format_exc())
        raise

# Load environment variables

load_dotenv()
BUGSINK_TOKEN = os.getenv("BUGSINK_TOKEN")
BUGSINK_API_URL = "http://localhost:8001/error"


# Import your modules safely

llm = safe_import("backend.llm")
vector_db = safe_import("backend.vector_db")


# FastAPI app
from fastapi import FastAPI, UploadFile, Form, Request

app = FastAPI()


#  Route decorator for Bugsink

def capture_bugsink(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
    return wrapper

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes

@app.get("/")
def read_root():
    return {"message": "Hello!"}

@app.post("/upload_pdf/")
@capture_bugsink
async def upload_pdf(file: UploadFile, fresh: bool = False):
    """
    Upload a PDF, extract text, chunk, and store embeddings.
    """
    num_chunks = vector_db.process_pdf(file.file, fresh=fresh)
    return {"num_chunks": num_chunks}

@app.post("/ask/")
@capture_bugsink
async def query_pdf(question: str = Form(...)):
    """
    Query the PDF content using semantic search.
    Returns top-k relevant chunks.
    """
    results = llm.answer_query(question)
    return {"query": question, "answer": results}
