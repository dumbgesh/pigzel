"""Interface contract for the planned Stage 2 Storyboard Director agent."""

from typing import Protocol, runtime_checkable

from ...schemas.creative import CreativeBrief, CreativeDirection
from ...schemas.storyboard import Storyboard


@runtime_checkable
class StoryboardDirector(Protocol):
    """Contract for converting an approved CreativeDirection into a Storyboard."""

    async def plan_storyboard(
        self,
        *,
        brief: CreativeBrief,
        direction: CreativeDirection,
        feedback: str | None = None,
    ) -> Storyboard:
        """Produce a validated Storyboard from an approved creative direction."""
        ...
