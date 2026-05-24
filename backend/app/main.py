from fastapi import FastAPI

app = FastAPI(
    title="CustodyAI Assistant",
    description="AI assistant for custody document Q&A and court-safe co-parenting messages.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "message": "CustodyAI Assistant backend is running"
    }
    