from fastapi import APIRouter, Form, HTTPException

from app.services.rewriter import rewrite_coparenting_message


router = APIRouter(
    prefix="/rewrite",
    tags=["Rewrite"]
)


@router.post("/message")
def rewrite_message(
    message: str = Form(...),
    tone: str = Form("neutral")
):
    allowed_tones = [
        "neutral",
        "firm",
        "documentation-focused",
        "cooperative",
        "brief"
    ]

    if tone not in allowed_tones:
        raise HTTPException(
            status_code=400,
            detail=f"Tone must be one of: {', '.join(allowed_tones)}"
        )

    rewritten_message = rewrite_coparenting_message(
        message=message,
        tone=tone
    )

    return {
        "original_message": message,
        "rewritten_message": rewritten_message,
        "tone": tone
    }