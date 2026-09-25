import re
from pathlib import Path

from google import genai
from google.genai import types

from .config import settings


def _safe_filename(text: str) -> str:
    """Convert text into a safe filename."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")

    return text[:80] or "panel"


def _get_gemini_client() -> genai.Client:
    """Create Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )


def generate_image_gemini(
    image_prompt: str,
    panel_number: int,
) -> str:
    """
    Generate one comic illustration using Gemini.
    """

    client = _get_gemini_client()

    prompt = f"""
Create a single comic-book illustration.

PANEL:
{panel_number}

VISUAL PROMPT:
{image_prompt}

Requirements:
- polished comic illustration
- strong readable composition
- expressive characters
- consistent visual identity
- appropriate lighting
- detailed environment
- no written text inside the image
- no speech bubbles
- no watermark
- suitable for a general-audience comic
"""

    response = client.models.generate_content(
        model=settings.GEMINI_IMAGE_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            response_format={
                "image": {
                    "aspect_ratio": "4:3",
                    "image_size": "1K",
                }
            },
        ),
    )

    output_path = (
        settings.PANEL_DIR
        / f"panel_{panel_number:02d}.png"
    )

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            image = part.as_image()
            image.save(output_path)

            return f"/static/panels/{output_path.name}"

    raise RuntimeError(
        f"Gemini did not return an image for panel {panel_number}."
    )


def generate_image(
    image_prompt: str,
    panel_number: int,
) -> str:
    """
    Main image-generation function.

    Supported providers:
    - gemini
    - diffusers
    """

    provider = settings.IMAGE_PROVIDER.lower()

    if provider == "gemini":
        return generate_image_gemini(
            image_prompt=image_prompt,
            panel_number=panel_number,
        )

    if provider == "diffusers":
        return generate_image_diffusers(
            image_prompt=image_prompt,
            panel_number=panel_number,
        )

    raise RuntimeError(
        f"Unknown IMAGE_PROVIDER: {provider}"
    )


def generate_image_diffusers(
    image_prompt: str,
    panel_number: int,
) -> str:
    """
    Optional Stable Diffusion implementation.

    Install the optional dependencies before using:
        pip install -r requirements-diffusers.txt

    This function is intentionally imported lazily so that the normal
    Gemini workflow does not require PyTorch/Diffusers.
    """

    try:
        import torch
        from diffusers import DiffusionPipeline
    except ImportError as exc:
        raise RuntimeError(
            "Diffusers is not installed. "
            "Install the optional Diffusers dependencies first."
        ) from exc

    dtype = (
        torch.float16
        if torch.cuda.is_available()
        else torch.float32
    )

    pipeline = DiffusionPipeline.from_pretrained(
        settings.STABLE_DIFFUSION_MODEL,
        torch_dtype=dtype,
    )

    if torch.cuda.is_available():
        pipeline = pipeline.to("cuda")

    output_path = (
        settings.PANEL_DIR
        / f"panel_{panel_number:02d}.png"
    )

    image = pipeline(
        prompt=image_prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
    ).images[0]

    image.save(output_path)

    return f"/static/panels/{output_path.name}"