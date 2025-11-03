# run_app.py
from pyngrok import ngrok
import uvicorn
import os
from dotenv import load_dotenv
from backend.main import app

# Load .env file (make sure it contains your NGROK_AUTHTOKEN)
load_dotenv()

# Set your ngrok auth token
ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))

if __name__ == "__main__":
    # Start ngrok tunnel for FastAPI (port 8000)
    public_url = ngrok.connect(8000)
    print(f"\n FastAPI is publicly available at: {public_url.public_url}\n")

    # Run FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000)

