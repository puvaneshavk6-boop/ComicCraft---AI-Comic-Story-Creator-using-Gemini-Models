from google import genai

from .config import settings
from .schemas import ComicOutline


def _get_client() -> genai.Client:
    """Create the Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Create a .env file and add your Gemini API key."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    panel_count: int = 5,
) -> ComicOutline:
    """
    Generate a structured panel-by-panel comic outline.

    Each panel contains:
    - panel number
    - title
    - scene description
    - image generation prompt
    """

    client = _get_client()

    prompt = f"""
You are the story-outline director for ComicCraft.

Create a coherent {panel_count}-panel comic outline.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

Requirements:

1. Create exactly {panel_count} panels.
2. Keep the same main character throughout.
3. Make the story have a clear beginning, middle, and ending.
4. Each panel must advance the story.
5. Scene descriptions should be visually useful.
6. Image prompts must describe the complete visual composition.
7. Do not include unsafe, graphic, or explicit material.
8. Do not put dialogue into image prompts.
9. Make image prompts suitable for an AI image-generation model.
10. Return only the requested structured data.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_FLASH_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ComicOutline.model_json_schema(),
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty outline response."
        )

    try:
        return ComicOutline.model_validate_json(response.text)
    except Exception as exc:
        raise RuntimeError(
            f"Could not parse Gemini outline response: {exc}"
        ) from exc