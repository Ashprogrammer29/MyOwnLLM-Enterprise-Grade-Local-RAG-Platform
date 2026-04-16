# MyOwnLLM: Enterprise-Grade Local RAG Platform

MyOwnLLM is a high-performance, containerized **Retrieval-Augmented Generation (RAG)** platform designed for secure, local document intelligence. It eliminates the privacy risks of cloud-based AI by processing all data and inference on local hardware using **Docker**, **Qdrant**, and **Ollama**.

## 🛠 Technical Architecture

The system is built on a microservices architecture to ensure scalability and separation of concerns:

### 1. Backend: FastAPI & Async Logic
The core engine is built on **FastAPI**, leveraging asynchronous endpoints for high-concurrency document processing.
* **Security:** Implemented **JWT (JSON Web Tokens)** for stateless, secure authentication.
* **ORM:** Utilized **SQLAlchemy** for structured user metadata stored in **PostgreSQL**.
* **Extraction:** Stream-based PDF text extraction using `pypdf`.

### 2. Vector Intelligence: Qdrant & Embeddings
The system implements a **Dense Retrieval** strategy for semantic understanding.
* **Model:** Text is transformed into 768-dimensional vectors using the `nomic-embed-text` model via the Ollama API.
* **Vector Store:** **Qdrant** is configured with **Cosine Similarity** metrics. 
* **Multi-Tenancy:** Each query is wrapped in a `Payload Condition` filter that restricts the search space to the specific `user_id`, preventing cross-user data leakage.

### 3. Reasoning Engine (LLM)
The retrieval pipeline follows the **Augment-Then-Generate** pattern:
1.  **Query Vectorization:** The user prompt is embedded into the same vector space as the documents.
2.  **Semantic Retrieval:** The top-k most relevant document chunks are retrieved from the vector store.
3.  **Context Injection:** Retrieved chunks are injected into a system prompt as ground-truth context.
4.  **Inference:** **Llama 3** processes the augmented prompt to generate an answer strictly based on the provided data.

## 🏗 Infrastructure (DevOps)
The platform is orchestrated into four primary services:
* `backend`: FastAPI application managing business logic and RAG coordination.
* `frontend`: Streamlit-based UI for seamless user interaction.
* `db`: PostgreSQL 15 instance for structured data storage.
* `qdrant`: High-performance vector database for unstructured data retrieval.

## 🚀 Deployment & Installation

### Prerequisites
* Docker & Docker Desktop
* Ollama (running on host) with `llama3` and `nomic-embed-text` models.

### Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Ashprogrammer29/MyOwnLLM.git](https://github.com/Ashprogrammer29/MyOwnLLM.git)
    cd MyOwnLLM
    ```
2.  **Spin up the Stack:**
    ```bash
    docker compose up -d --build
    ```
3.  **Access:**
    * **Frontend UI:** `http://localhost:8501`
    * **Interactive API Docs (Swagger):** `http://localhost:8000/docs`

## 🚀 Future Roadmap
* **Hybrid Search:** Integrating BM25 keyword matching alongside Qdrant's vector search.
* **Re-Ranking:** Implementing a Cross-Encoder to refine the precision of retrieved context chunks.
* **Asynchronous Workers:** Moving ingestion tasks to **Celery + Redis** for background processing.

---

### 🚩 Project Status Update
As of **April 2026**, this project is feature-complete. The primary milestones reached include:
* **Fully Integrated Auth:** JWT-secured endpoints with PostgreSQL persistence.
* **Verified RAG Pipeline:** Successful integration between the `QdrantManager` and Ollama inference.
* **Containerized Networking:** Optimized Docker bridge networking for MLOps efficiency.
