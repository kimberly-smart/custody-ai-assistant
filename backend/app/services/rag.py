import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY is not set in .env")

if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT is not set in .env")

if not AZURE_OPENAI_CHAT_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT is not set in .env")


client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT
)


def generate_grounded_answer(
    question: str,
    retrieved_chunks: List[Dict]
) -> str:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not retrieved_chunks:
        return "The uploaded documents do not provide enough information to answer this question."

    context_sections = []

    for chunk in retrieved_chunks:
        context_sections.append(
            f"[Document ID: {chunk['document_id']}, "
            f"Page: {chunk['page_number']}, "
            f"Chunk ID: {chunk['chunk_id']}]\n"
            f"{chunk['content']}"
        )

    context = "\n\n---\n\n".join(context_sections)

    instructions = """
You are a document-grounded assistant for custody and divorce documents.

Answer only from the provided document excerpts.
Do not give legal advice.
Do not infer facts that are not present in the excerpts.
If the excerpts do not contain enough information, state that the uploaded documents do not provide enough information to answer.
Include the relevant document ID and page number in the answer.
Keep the answer clear and concise.
"""

    prompt = f"""
DOCUMENT EXCERPTS:
{context}

USER QUESTION:
{question}
"""

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions=instructions,
        input=prompt
    )

    return response.output_text