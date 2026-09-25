from typing import List

from .schemas import (
    ComicOutline,
    ComicStory,
    ComicPanel,
)


def build_comic_layout(
    outline: ComicOutline,
    story: ComicStory,
    image_paths: List[str],
) -> List[ComicPanel]:
    """
    Combine:
    - outline information
    - story information
    - generated images

    into final comic panels.
    """

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    outline_by_panel = {
        panel.panel_number: panel
        for panel in outline.panels
    }

    layout: List[ComicPanel] = []

    for index, image_path in enumerate(
        image_paths,
        start=1,
    ):
        outline_panel = outline_by_panel.get(index)

        story_panel = story_by_panel.get(index)

        if not outline_panel:
            raise RuntimeError(
                f"Missing outline panel {index}."
            )

        if not story_panel:
            raise RuntimeError(
                f"Missing story panel {index}."
            )

        layout.append(
            ComicPanel(
                panel_number=index,
                title=story_panel.title,
                image_path=image_path,
                scene_description=(
                    outline_panel.scene_description
                ),
                caption=story_panel.caption,
                narration=story_panel.narration,
                dialogue=story_panel.dialogue,
                image_prompt=outline_panel.image_prompt,
            )
        )

    return layout