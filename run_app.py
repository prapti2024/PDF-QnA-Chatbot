import subprocess
import time
import requests
import os

FASTAPI_MODULE = "backend.main:app"
FASTAPI_URL = "http://127.0.0.1:8000"  # Use 127.0.0.1 on Windows

def start_fastapi():
    """Start FastAPI as a subprocess and return the Popen object."""
    return subprocess.Popen(
        ["uvicorn", FASTAPI_MODULE, "--host", "127.0.0.1", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy()
    )

def wait_for_fastapi(timeout=30):
    """Wait until FastAPI is ready or timeout (seconds)."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            res = requests.get(f"{FASTAPI_URL}/docs")
            if res.status_code == 200:
                print("FastAPI is up!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

def start_streamlit():
    """Start Streamlit as a subprocess."""
    subprocess.Popen(["streamlit", "run", "frontend/app.py"], shell=True)

if __name__ == "__main__":
    fastapi_proc = start_fastapi()
    print("Starting FastAPI...")

    if wait_for_fastapi(timeout=30):
        start_streamlit()
        print("Streamlit started!")
    else:
        print("FastAPI did not start in time.")
        fastapi_proc.terminate()

    