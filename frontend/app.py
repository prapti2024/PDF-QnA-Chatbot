import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Chat with PDF ", layout="centered")
st.title("Chat with Your PDF")

# --- Upload PDF ---
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Uploading and embedding PDF..."):
        files = {"file": uploaded_file.getvalue()}
        res = requests.post(f"{FASTAPI_URL}/upload_pdf/", files={"file": (uploaded_file.name, uploaded_file, "application/pdf")})
    if res.status_code == 200:
        st.success(res.json().get("message", "PDF uploaded successfully!"))
    else:
        st.error("Failed to upload PDF.")

# --- Ask Question ---
st.subheader("Ask a question about your uploaded PDF")
question = st.text_input("Your question")

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            res = requests.post(f"{FASTAPI_URL}/ask/", data={"question": question})
            if res.status_code == 200:
                st.markdown("### 💬 Answer:")
                st.write(res.json()["answer"])
            else:
                st.error("Something went wrong while querying.")
