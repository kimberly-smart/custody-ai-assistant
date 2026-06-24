import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import documents, chat, rewrite
from app.db.database import engine, Base
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

app = FastAPI(
    title="CustodyAI Assistant",
    description="AI assistant for custody document Q&A and court-safe co-parenting messages.",
    version="0.1.0",
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(rewrite.router)

@app.get("/")
def root():
    return {
        "message": "CustodyAI Assistant backend is running"
    }
