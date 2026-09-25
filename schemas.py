from typing import List

from pydantic import BaseModel, Field


class ComicRequest(BaseModel):
    """JSON request for comic generation."""

    story_prompt: str = Field(
        min_length=3,
        max_length=2000,
    )

    character_name: str = Field(
        min_length=1,
        max_length=100,
    )

    setting: str = Field(
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        min_length=1,
        max_length=100,
    )

    art_style: str = Field(
        min_length=1,
        max_length=100,
    )

    panel_count: int = Field(
        default=5,
        ge=3,
        le=8,
    )


class PanelOutline(BaseModel):
    """AI-generated outline for one comic panel."""

    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    """Complete comic outline."""

    panels: List[PanelOutline]


class PanelStory(BaseModel):
    """Narration and dialogue for one panel."""

    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: List[str]


class ComicStory(BaseModel):
    """Complete comic story."""

    panels: List[PanelStory]


class ComicPanel(BaseModel):
    """Final panel used by the frontend and PDF exporter."""

    panel_number: int
    title: str
    image_path: str
    scene_description: str
    caption: str
    narration: str
    dialogue: List[str]
    image_prompt: str


class GenerateResponse(BaseModel):
    """JSON response returned by the generation API."""

    success: bool
    message: str
    panels: List[ComicPanel]
    pdf_url: str