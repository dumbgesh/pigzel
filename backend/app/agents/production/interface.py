"""Interface contract for the planned Stage 3 Production Planner agent."""

from typing import Protocol, runtime_checkable

from ..production.assembler import ProductionConfig
from ...schemas.production import GenerationJob


@runtime_checkable
class ProductionPlanner(Protocol):
    """Contract for planning per-scene generation jobs in Stage 3."""

    async def plan_jobs(
        self,
        *,
        project_version_id: str,
        scene_ids: list[str],
        config: ProductionConfig,
        target_scene_id: str | None = None,
    ) -> list[GenerationJob]:
        """Create ordered GenerationJob specs for all scenes or a single target scene."""
        ...
