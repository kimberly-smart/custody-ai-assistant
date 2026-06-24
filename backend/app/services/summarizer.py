import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY is not set.")

if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT is not set.")

if not AZURE_OPENAI_CHAT_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT is not set.")

client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT,
)


def generate_document_summary(filename: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "No text chunks were found for this document."

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Page {chunk['page_number']}, Chunk {chunk['chunk_index']}]\n"
            f"{chunk['content']}"
        )

    full_context = "\n\n".join(context_parts)

    # Demo safety limit so very large documents do not exceed model context.
    max_chars = 16000
    if len(full_context) > max_chars:
        full_context = full_context[:max_chars]

    instructions = """
    You are a document-grounded assistant for custody and divorce documents.

    Your task is to summarize the uploaded document using only the provided document text.

    Rules:
    - Do not give legal advice.
    - Do not invent facts.
    - If the document text is incomplete, say that the summary is based on the available extracted text.
    - Write a clear, brief summary.
    - Organize the summary into practical sections when possible.
    - Mention important topics such as custody, parenting time, child support, medical expenses, communication, decision-making, and enforcement only if they appear in the provided text.
    """

    prompt = f"""
    DOCUMENT NAME:
    {filename}

    DOCUMENT TEXT:
    {full_context}

    Please provide a brief but useful summary of this document.
    """

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions=instructions,
        input=prompt,
    )

    return response.output_text