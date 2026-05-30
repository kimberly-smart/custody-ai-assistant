from fastapi import FastAPI
from app.routes import documents
from app.db.database import engine, Base
from app.models.document import Document

app = FastAPI(
    title="CustodyAI Assistant",
    description="AI assistant for custody document Q&A and court-safe co-parenting messages.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)
app.include_router(documents.router)

@app.get("/")
def root():
    return {
        "message": "CustodyAI Assistant backend is running"
    }
