import re
from datetime import datetime
from pathlib import Path
from typing import List

from fpdf import FPDF

from .config import settings
from .schemas import ComicPanel


def _clean_text(text: str) -> str:
    """
    Make text safer for the built-in PDF font.
    """
    return text.encode(
        "latin-1",
        errors="replace",
    ).decode("latin-1")


def _safe_filename(text: str) -> str:
    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text,
    )

    return text[:80] or "comic"


def save_pdf(
    layout: List[ComicPanel],
    title: str = "ComicCraft Comic",
) -> str:
    """
    Create a multi-page PDF.

    Each comic panel receives one PDF page.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{_safe_filename(title)}_{timestamp}.pdf"
    )

    output_path = (
        settings.EXPORT_DIR / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:
        pdf.add_page()

        # Title
        pdf.set_font(
            "Arial",
            "B",
            18,
        )

        pdf.cell(
            0,
            12,
            _clean_text(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            ),
            ln=True,
        )

        # Image
        image_file = (
            settings.BASE_DIR
            / panel.image_path.lstrip("/")
            .replace("/", str(Path("/")))
        )

        # More reliable local path construction
        relative_static = panel.image_path.replace(
            "/static/",
            "",
        ).lstrip("/")

        image_file = (
            settings.STATIC_DIR
            / relative_static
        )

        if image_file.exists():
            pdf.image(
                str(image_file),
                x=15,
                y=None,
                w=180,
            )

        pdf.ln(8)

        # Scene
        pdf.set_font(
            "Arial",
            "I",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel.scene_description
            ),
        )

        pdf.ln(3)

        # Caption
        pdf.set_font(
            "Arial",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                f"Caption: {panel.caption}"
            ),
        )

        pdf.ln(2)

        # Narration
        pdf.set_font(
            "Arial",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                f"Narration: {panel.narration}"
            ),
        )

        # Dialogue
        if panel.dialogue:
            pdf.ln(2)

            pdf.set_font(
                "Arial",
                "B",
                11,
            )

            pdf.cell(
                0,
                6,
                "Dialogue:",
                ln=True,
            )

            pdf.set_font(
                "Arial",
                "",
                11,
            )

            for line in panel.dialogue:
                pdf.multi_cell(
                    0,
                    6,
                    _clean_text(
                        f"• {line}"
                    ),
                )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )