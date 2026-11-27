"""Stage 1 — Creative Intelligence API endpoints."""

from fastapi import APIRouter, Depends

from ...agents.creative.agent import CreativeIntelligenceAgent
from ...core.config import Settings, get_settings
from ...ingestion.brief_normalizer import normalize_brief
from ...model_gateway.llm.factory import get_llm_provider
from ...schemas.creative import CreativeBrief, CreativeIntelligenceResult

router = APIRouter(prefix="/creative", tags=["creative"])


def get_creative_agent(settings: Settings = Depends(get_settings)) -> CreativeIntelligenceAgent:
    """Build a CreativeIntelligenceAgent wired to the configured LLM provider."""
    provider = get_llm_provider(settings)
    return CreativeIntelligenceAgent(llm_provider=provider)


@router.post("/concepts", response_model=CreativeIntelligenceResult)
async def generate_creative_concepts(
    brief: CreativeBrief,
    agent: CreativeIntelligenceAgent = Depends(get_creative_agent),
) -> CreativeIntelligenceResult:
    """Validate a CreativeBrief and generate three distinct creative concepts."""
    normalized_brief = normalize_brief(brief)
    return await agent.run(normalized_brief)
