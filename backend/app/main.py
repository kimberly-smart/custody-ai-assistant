from fastapi import FastAPI
from app.routes import documents

app = FastAPI(
    title="CustodyAI Assistant",
    description="AI assistant for custody document Q&A and court-safe co-parenting messages.",
    version="0.1.0",
)

app.include_router(documents.router)

@app.get("/")
def root():
    return {
        "message": "CustodyAI Assistant backend is running"
    }
