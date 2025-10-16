# llm.py
# llm.py
from .vector_db import init_db
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama2:7b",
    temperature=0,
)

def get_retriever(k: int = 3):
    """Load persisted Chroma DB and return a retriever for semantic search."""
    db = init_db(fresh=False)
    return db.as_retriever(search_kwargs={"k": k})

def query_text(query: str, k: int = 3):
    """Return top-k relevant chunks for a given query."""
    retriever = get_retriever(k=k)
    results = retriever.invoke(query)
    return [r.page_content for r in results]

def answer_query(query: str, k: int = 3):
    """Generate answer using Ollama LLM with retrieved chunks."""
    chunks = query_text(query, k=k)
    context = "\n\n".join(chunks)

    prompt = f"""
You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question:
{query}

Answer:"""

    # Send prompt to Ollama (replace 'llama7b' with your installed model name)
    messages=[{"role": "user", "content": prompt}]
    response = llm.invoke(messages)
    return response.content
