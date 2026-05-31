import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)

if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY is not set in .env")

if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT is not set in .env")

if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not set in .env")


client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT
)


def create_embedding(text: str) -> List[float]:
    if not text or not text.strip():
        raise ValueError("Cannot create an embedding for empty text.")

    response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=text
    )

    return response.data[0].embedding