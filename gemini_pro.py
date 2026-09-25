import json
from typing import List

from google import genai

from .config import settings
from .schemas import ComicOutline, ComicStory


def _get_client() -> genai.Client:
    """Create Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )


def generate_story(
    outline: ComicOutline,
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
) -> ComicStory:
    """
    Expand a comic outline into narration, captions and dialogue.
    """

    client = _get_client()

    outline_json = json.dumps(
        outline.model_dump(),
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are the lead comic-book writer for ComicCraft.

Create the complete narration and dialogue for the supplied comic outline.

ORIGINAL STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

OUTLINE:
{outline_json}

Requirements:

1. Preserve the exact panel order.
2. Create one story object for every outline panel.
3. Keep character details consistent.
4. Write concise comic-style narration.
5. Write a short caption for each panel.
6. Add natural dialogue where appropriate.
7. Do not make dialogue overly long.
8. Keep the story suitable for a general audience.
9. Do not introduce unnecessary characters.
10. Return structured data only.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_PRO_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ComicStory.model_json_schema(),
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty story response."
        )

    try:
        return ComicStory.model_validate_json(response.text)
    except Exception as exc:
        raise RuntimeError(
            f"Could not parse Gemini story response: {exc}"
        ) from exc