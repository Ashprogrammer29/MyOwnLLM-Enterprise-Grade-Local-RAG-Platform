import streamlit as st
import requests

# Configuration
# 'fastapi_backend' MUST match the service name in your docker-compose.yml
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="MyOwnLLM", layout="wide")
st.title("MyOwnLLM: Personal RAG Assistant")

# --- Session State Initialization ---
if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Authentication ---
with st.sidebar:
    st.header("🔐 Authentication")
    if not st.session_state.token:
        email = st.text_input("Email", value="aswin@dev.com")
        password = st.text_input("Password", type="password", value="aswindev")

        if st.button("Login"):
            try:
                # IMPORTANT: FastAPI OAuth2 expects data (form-data), not json
                resp = requests.post(
                    f"{BACKEND_URL}/token",
                    data={"username": email, "password": password},
                    timeout=10
                )

                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.token = data.get("access_token")
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    # Capture the actual error message from backend
                    error_detail = resp.json().get("detail", "Login failed")
                    st.error(f"Error {resp.status_code}: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach Backend. Is the FastAPI container running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.success("Connected to Backend")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

    # --- Sidebar: Document Upload ---
    if st.session_state.token:
        st.divider()
        st.header("📂 Knowledge Base")
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

        if uploaded_file and st.button("Index Document"):
            with st.spinner("Processing PDF and generating embeddings..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                # Wrap the file in the correct format for FastAPI 'File'
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                # Data for the 'Form' field
                payload = {"filename": uploaded_file.name}

                try:
                    res = requests.post(
                        f"{BACKEND_URL}/upload",
                        headers=headers,
                        files=files,
                        data=payload,
                        timeout=60  # Embedding takes time
                    )
                    if res.status_code == 200:
                        st.success(f"Successfully indexed {uploaded_file.name}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Upload Error: {e}")

# --- Main Chat Interface ---
if not st.session_state.token:
    st.info("Please login from the sidebar to start chatting.")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask me anything about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response from Backend
        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    headers=headers,
                    json={"message": prompt},
                    timeout=60
                )
                if response.status_code == 200:
                    res_json = response.json()
                    answer = res_json.get("answer", "No answer generated.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    # Optional: Display sources
                    if "sources" in res_json and res_json["sources"]:
                        st.caption(f"Sources: {', '.join(res_json['sources'])}")
                else:
                    st.error(f"Chat Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")