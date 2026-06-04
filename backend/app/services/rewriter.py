import os

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


def rewrite_coparenting_message(message: str, tone: str = "neutral") -> str:
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    instructions = """
You rewrite co-parenting messages in a calm, factual, and documentation-friendly tone.

Rules:
- Preserve the user's factual concern and requested action.
- Remove insults, profanity, threats, sarcasm, and emotionally escalatory language.
- Do not invent facts, dates, events, legal rights, or court-order provisions.
- Do not accuse the other parent of misconduct unless the user explicitly stated a confirmed fact.
- Do not provide legal advice or say that conduct violates a court order.
- Write the result as a message the user can send directly.
- Keep it concise and natural.
"""

    prompt = f"""
TONE REQUESTED: {tone}

ORIGINAL MESSAGE:
{message}

Rewrite this message for co-parent communication.
"""

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions=instructions,
        input=prompt
    )

    return response.output_text