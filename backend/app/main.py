from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import documents, chat
from app.db.database import engine, Base
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

app = FastAPI(
    title="CustodyAI Assistant",
    description="AI assistant for custody document Q&A and court-safe co-parenting messages.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {
        "message": "CustodyAI Assistant backend is running"
    }
