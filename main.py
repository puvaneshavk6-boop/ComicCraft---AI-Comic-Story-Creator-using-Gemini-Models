from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import router


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI Comic Story Creator powered by "
        "FastAPI and Gemini."
    ),
    version="1.0.0",
)


# Static files
app.mount(
    "/static",
    StaticFiles(
        directory=str(
            settings.STATIC_DIR
        )
    ),
    name="static",
)


# Application routes
app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""

    return {
        "status": "ok",
        "application": settings.APP_NAME,
    }