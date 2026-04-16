import io
from fastapi import FastAPI, Depends, HTTPException, status, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.db import models, session, crud, schemas
from app.auth import security
from app.core.rag_service import RagService
from app.core.qdrant_manager import QdrantManager

app = FastAPI(title="MyOwnLLM API")
rag_service = RagService()
qdrant_manager = QdrantManager()

models.Base.metadata.create_all(bind=session.engine)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(session.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/upload")
async def upload_file(file: bytes = File(...), filename: str = Form(...),
                      current_user: models.User = Depends(security.get_current_user)):
    pdf_stream = io.BytesIO(file)
    reader = PdfReader(pdf_stream)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

    qdrant_manager.index_document(text=text, filename=filename, user_id=str(current_user.id))
    return {"message": f"Successfully indexed {filename}"}


@app.post("/chat")
async def chat(request: schemas.ChatRequest, current_user: models.User = Depends(security.get_current_user)):
    answer, sources = await rag_service.get_answer(request.message, str(current_user.id))
    return {"answer": answer, "sources": sources}


@app.get("/health")
def health(): return {"status": "healthy"}