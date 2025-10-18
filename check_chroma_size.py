from backend.vector_db import init_db
import os

def get_db_size_mb(directory="pdf_vector_db"):
    """Return total size of Chroma DB folder in MB."""
    total = 0
    
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    size_mb = total / (1024 * 1024)
    print(f"Chroma DB size: {size_mb:.2f} MB")
    return size_mb

def get_db_stats():
    """Show basic info about the Chroma collection."""
    db = init_db(fresh=False)  # connect to existing DB
    collection = db.get()
    num_docs = len(collection["ids"])
    print(f"Total stored chunks/documents: {num_docs}")
    return num_docs


if __name__== "__main__":
    print(get_db_stats)
    print(get_db_size_mb())
    