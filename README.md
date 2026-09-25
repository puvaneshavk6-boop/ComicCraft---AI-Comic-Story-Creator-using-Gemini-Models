# ComicCraft

AI Comic Story Creator using FastAPI and Gemini.

ComicCraft converts a user story idea into:

1. Structured comic outline
2. Panel-by-panel narration
3. Character dialogue
4. AI-generated illustrations
5. Comic preview
6. Downloadable PDF

---

# Project Architecture

Frontend:

- HTML
- CSS
- JavaScript
- Jinja2

Backend:

- FastAPI
- Pydantic
- Uvicorn

AI:

- Gemini structured text generation
- Gemini image generation

Optional:

- Hugging Face Diffusers
- Stable Diffusion

Export:

- FPDF

---

# Project Structure

ComicCraft/

    app/
        __init__.py
        main.py
        routes.py
        config.py
        schemas.py
        gemini_flash.py
        gemini_pro.py
        image_generator.py
        layout_builder.py
        exporters.py

    templates/
        index.html
        comic_preview.html
        export_success.html

    static/
        css/
            style.css
        js/
            script.js
        panels/
        exports/

    tests/
        test_app.py

    .env.example
    .gitignore
    requirements.txt
    README.md


# Requirements

Recommended:

Python 3.11+

VS Code

A Gemini API key


# Windows Installation

Open the ComicCraft folder in VS Code.

Open:

Terminal > New Terminal


Create a virtual environment:

    py -3.11 -m venv .venv


Activate it:

    .venv\Scripts\Activate.ps1


If PowerShell blocks activation, use:

    .venv\Scripts\activate.bat


Upgrade pip:

    python -m pip install --upgrade pip


Install dependencies:

    pip install -r requirements.txt


# Environment Configuration

Copy:

    .env.example

and rename the copy to:

    .env


Open .env.

Set:

    GEMINI_API_KEY=YOUR_API_KEY

Recommended image provider:

    IMAGE_PROVIDER=gemini


# Start the Application

Run:

    uvicorn app.main:app --reload


Open:

    http://127.0.0.1:8000


API documentation:

    http://127.0.0.1:8000/docs


Health check:

    http://127.0.0.1:8000/health


# How Comic Generation Works

The /generate route executes:

    generate_outline()
        |
        v
    generate_story()
        |
        v
    generate_image()
        |
        v
    build_comic_layout()
        |
        v
    save_pdf()


# JSON API

Endpoint:

    POST /generate-comic/json


Example request:

    {
        "story_prompt": "A brave fox discovers a magical door.",
        "character_name": "Finn",
        "setting": "enchanted forest",
        "tone": "adventurous",
        "art_style": "comic book",
        "panel_count": 5
    }


# Test Image

Open:

    http://127.0.0.1:8000/test-image


You can also provide a prompt:

    http://127.0.0.1:8000/test-image?prompt=A%20robot%20exploring%20Mars


# Run Tests

Install test dependencies:

    pip install pytest httpx


Run:

    pytest -q


The tests do not require Gemini API calls.

They verify:

- Health endpoint
- Homepage
- Request validation


# Optional Stable Diffusion

The default image provider is Gemini.

To use the optional Diffusers implementation:

    pip install -r requirements-diffusers.txt


Then change .env:

    IMAGE_PROVIDER=diffusers


You can also change:

    STABLE_DIFFUSION_MODEL=runwayml/stable-diffusion-v1-5


Stable Diffusion can require significant RAM/VRAM and may take much longer than Gemini image generation.


# Common Problems

## GEMINI_API_KEY missing

Make sure:

1. .env exists.
2. GEMINI_API_KEY is present.
3. The API key is valid.
4. Restart Uvicorn after changing .env.


## Port already in use

Use:

    uvicorn app.main:app --reload --port 8001


Then open:

    http://127.0.0.1:8001


## Images are not appearing

Check:

    static/panels/


The generated images should be saved there.


## PDF is not generated

Check:

    static/exports/


Also verify that:

    pip install fpdf2


has completed successfully.


# Development

Start the server:

    uvicorn app.main:app --reload


The --reload option automatically restarts the development server when Python files change.


# Production

For deployment, consider:

- HTTPS
- authentication
- rate limiting
- background jobs
- persistent database
- object storage for images
- logging
- monitoring
- API-key protection
- request size limits


# ComicCraft Workflow

User enters:

    Story Prompt
    Character
    Setting
    Tone
    Art Style
    Panel Count

        ↓

Gemini outline generation

        ↓

Panel-by-panel story generation

        ↓

AI image generation

        ↓

Comic layout

        ↓

PDF export

        ↓

Comic preview

        ↓

Download PDF