from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
EXPORTS_DIR = BASE_DIR / "exports"

EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FastAPI Router
# ============================================================

router = APIRouter()

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ============================================================
# Helper functions
# ============================================================

def _get_settings() -> Dict[str, Any]:
    """
    Load application settings if config.py provides them.
    The application can still start if settings are unavailable.
    """
    try:
        from .config import settings

        if hasattr(settings, "model_dump"):
            return settings.model_dump()

        if hasattr(settings, "dict"):
            return settings.dict()

        if hasattr(settings, "__dict__"):
            return dict(settings.__dict__)

    except Exception:
        pass

    return {}


def _get_value(data: Any, key: str, default: Any = None) -> Any:
    """
    Safely read a value from either a dictionary or an object.
    """
    if isinstance(data, dict):
        return data.get(key, default)

    return getattr(data, key, default)


def _normalise_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert the incoming ComicCraft JSON payload into a predictable format.
    """

    return {
        "story_prompt": str(
            payload.get("story_prompt", "")
        ).strip(),

        "character_name": str(
            payload.get("character_name", "")
        ).strip(),

        "setting": str(
            payload.get("setting", "")
        ).strip(),

        "tone": str(
            payload.get("tone", "")
        ).strip(),

        "art_style": str(
            payload.get("art_style", "")
        ).strip(),

        "panel_count": int(
            payload.get("panel_count", 5)
        ),
    }


def _validate_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Validate ComicCraft generation input.
    """

    story_prompt = payload.get("story_prompt", "").strip()

    if not story_prompt:
        return "story_prompt is required."

    try:
        panel_count = int(payload.get("panel_count", 5))
    except (TypeError, ValueError):
        return "panel_count must be an integer."

    if panel_count < 1:
        return "panel_count must be at least 1."

    if panel_count > 12:
        return "panel_count cannot be greater than 12."

    return None


def _generate_outline(payload: Dict[str, Any]) -> Any:
    """
    Generate the comic outline using the Gemini integration.
    """

    try:
        from .gemini_flash import generate_outline
    except ImportError as exc:
        raise RuntimeError(
            "Gemini integration could not be imported."
        ) from exc

    try:
        return generate_outline(
            story_prompt=payload["story_prompt"],
            character_name=payload["character_name"],
            setting=payload["setting"],
            tone=payload["tone"],
            art_style=payload["art_style"],
            panel_count=payload["panel_count"],
        )

    except TypeError:
        # Supports implementations where generate_outline
        # accepts a single dictionary.
        return generate_outline(payload)


def _generate_images(outline: Any, payload: Dict[str, Any]) -> Any:
    """
    Generate comic panel images when the image generation module
    is available.
    """

    try:
        from .image_generator import generate_panel_images
    except (ImportError, AttributeError):
        return []

    try:
        return generate_panel_images(
            outline=outline,
            art_style=payload.get("art_style", ""),
        )

    except TypeError:
        try:
            return generate_panel_images(outline)
        except Exception:
            return []

    except Exception:
        return []


def _export_pdf(
    outline: Any,
    payload: Dict[str, Any],
    images: Any = None,
) -> Optional[str]:
    """
    Export the generated comic to PDF.

    Returns the generated filename/path when available.
    """

    try:
        from .exporters import save_pdf
    except (ImportError, AttributeError):
        return None

    try:
        result = save_pdf(
            outline=outline,
            images=images or [],
            payload=payload,
            output_dir=EXPORTS_DIR,
        )
    except TypeError:
        try:
            result = save_pdf(
                outline,
                images or [],
                EXPORTS_DIR,
            )
        except Exception:
            return None
    except Exception:
        return None

    if result is None:
        return None

    return str(result)


# ============================================================
# Homepage
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    """
    Render ComicCraft homepage.
    """

    settings = _get_settings()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "settings": settings,
        },
    )


# ============================================================
# Health Check
# ============================================================

@router.get("/health")
async def health():
    """
    Health-check endpoint.
    """

    return {
        "status": "ok",
        "service": "ComicCraft",
    }


# ============================================================
# Generate Comic - HTML form
# ============================================================

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_complete_comic(
    request: Request,
):
    """
    Generate a complete comic from the HTML form.
    """

    try:
        form = await request.form()

        payload = {
            "story_prompt": str(
                form.get("story_prompt", "")
            ),

            "character_name": str(
                form.get("character_name", "")
            ),

            "setting": str(
                form.get("setting", "")
            ),

            "tone": str(
                form.get("tone", "")
            ),

            "art_style": str(
                form.get("art_style", "")
            ),

            "panel_count": int(
                form.get("panel_count", 5)
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid form data: {exc}",
        ) from exc

    payload = _normalise_payload(payload)

    validation_error = _validate_payload(payload)

    if validation_error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "settings": _get_settings(),
                "error": validation_error,
                "form_data": payload,
            },
            status_code=422,
        )

    try:
        outline = _generate_outline(payload)

        images = _generate_images(
            outline,
            payload,
        )

        pdf_file = _export_pdf(
            outline,
            payload,
            images,
        )

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "settings": _get_settings(),
                "error": str(exc),
                "form_data": payload,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "request": request,
            "settings": _get_settings(),
            "payload": payload,
            "outline": outline,
            "images": images,
            "pdf_file": pdf_file,
        },
    )


# ============================================================
# Generate Comic - JSON API
# ============================================================

@router.post(
    "/generate-comic/json",
)
async def generate_comic_json(
    payload: Dict[str, Any] = Body(...),
):
    """
    JSON API endpoint used by frontend JavaScript and tests.
    """

    payload = _normalise_payload(payload)

    validation_error = _validate_payload(payload)

    if validation_error:
        return JSONResponse(
            status_code=422,
            content={
                "detail": validation_error,
            },
        )

    try:
        outline = _generate_outline(payload)

        images = _generate_images(
            outline,
            payload,
        )

        pdf_file = _export_pdf(
            outline,
            payload,
            images,
        )

        return {
            "success": True,
            "message": "Comic generated successfully.",
            "payload": payload,
            "outline": outline,
            "images": images,
            "pdf_file": pdf_file,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": str(exc),
            },
        )


# ============================================================
# Test Image
# ============================================================

@router.get(
    "/test-image",
    response_class=HTMLResponse,
)
async def test_image(request: Request):
    """
    Simple image-generation test page.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "settings": _get_settings(),
            "test_image": True,
        },
    )


# ============================================================
# Download generated files
# ============================================================

@router.get(
    "/download/{filename}",
)
async def download_file(
    filename: str,
):
    """
    Download a generated export file.
    """

    # Prevent path traversal.
    safe_name = Path(filename).name

    file_path = EXPORTS_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return FileResponse(
        path=str(file_path),
        filename=safe_name,
    )


# ============================================================
# Export Success
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    filename: Optional[str] = None,
):
    """
    Display export-success page.
    """

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "filename": filename,
            "download_url": (
                f"/download/{Path(filename).name}"
                if filename
                else None
            ),
        },
    )