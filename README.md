# Pigzel

Open-source, modular AI-powered video production platform.

## Purpose

Convert user ideas, instructions, and reference materials into complete videos using a multi-stage AI workflow with human-in-the-loop control.

Intended for creators, agencies, production studios, social media teams, and developers.

## Current Development Status

**Stage: Milestone 2 (Partial) — Stage 1 Creative Intelligence Implemented (Mock Provider)**

- **Implemented**: FastAPI backend foundation (`/api/v1/health`, `/api/v1/creative/concepts`), `CreativeBrief` ingestion/validation, `CreativeConcept` / `CreativeDirection` / `CreativeIntelligenceResult` schemas, provider-independent `LLMProvider` gateway with `MockLLMProvider` for local testing, `CreativeIntelligenceAgent`, and `pytest` suite (23 tests passing).
- **Not Yet Implemented**: Live hosted/local LLM adapters, Stage 1 human approval persistence/orchestrator, Stage 2 (Visual Planning), Stage 3 (Video Production), database/storage persistence, and Next.js frontend.

> **Note**: The currently wired `MockLLMProvider` (`is_mock: true`) returns deterministic structured responses for development and testing without API keys—it is not real AI inference.

## Three-Stage Pipeline (Planned)

Pigzel separates video production into three distinct, human-approved stages:

1. **Stage 1 — Creative Intelligence**
   - Analyze user requirements, instructions, and reference materials.
   - Generate multiple distinct creative concepts and narratives.
   - Produce a recommended creative direction with structured production instructions.
2. **Stage 2 — Visual Planning**
   - Convert approved creative directions into structured storyboards.
   - Break narratives into individual scenes with shot types, camera movements, lighting, and environments.
   - Generate visual references and maintain a consistent visual bible.
3. **Stage 3 — Video Production**
   - Plan scene-generation jobs from approved storyboards.
   - Coordinate image, video, and audio generation providers.
   - Support independent scene-level regeneration and assemble final video exports.

Human approval is required between major stages.

## Planned Capabilities

- **Formats**: Advertisements, social media content, promotional videos, explainer videos, short films, brand films, and other creative formats.
- **Modes**: Simple mode (guided end-to-end) and Advanced mode (granular storyboard and scene control).
- **Model Strategy**: Open-weight models first, hosted inference APIs, optional local inference, and proprietary fallbacks where justified—all behind a provider-independent model gateway.
- **Outputs**: Individual scene clips and fully assembled final videos, with versioned creative artifacts.
- **Design Philosophy**: Modular, model-independent, extensible, schema-validated, and reproducible.

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, HTTPX, Pytest
- **Frontend (Planned)**: Next.js, TypeScript
- **Infrastructure (Planned as needed)**: PostgreSQL, Redis, S3-compatible storage, FFmpeg, Docker

## Repository Structure

```text
pigzel/
├── backend/         # FastAPI application, agents, orchestrator, model gateway, schemas
├── frontend/        # Next.js + TypeScript web interface (planned)
├── docs/            # Architecture, PRD, agent specs, model strategy, workflow, roadmap, ADRs
├── examples/        # Sample project briefs and pipeline examples
├── scripts/         # Developer and maintenance scripts
├── .env.example     # Environment variable template
├── LICENSE          # MIT License
└── README.md
```

## Documentation

- [Architecture](docs/architecture.md)
- [Product Requirements](docs/product-requirements.md)
- [Data Contracts](docs/data-contracts.md)
- [Agent Specifications](docs/agent-specifications.md)
- [Stage 1 Spec — Creative Intelligence](docs/stage-1-creative-intelligence.md)
- [Model Strategy](docs/model-strategy.md)
- [Workflow](docs/workflow.md)
- [Roadmap](docs/roadmap.md)
- [Architectural Decisions](docs/decisions.md)

## Getting Started (Contributors)

1. Ensure **Python 3.12+** is installed.
2. Copy `.env.example` to `.env` (defaults to `PIGZEL_LLM_PROVIDER=mock` if unset).
3. Install backend dependencies in editable mode from `backend/`:
   ```bash
   cd backend
   pip install -e ".[dev]"
   ```
4. Run the backend API:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   - Health check: `GET http://127.0.0.1:8000/api/v1/health`
   - Generate concepts: `POST http://127.0.0.1:8000/api/v1/creative/concepts`
5. Run the test suite (no external API keys required):
   ```bash
   cd backend
   pytest -v
   ```

### Example Stage 1 Request & Output

**Request (`POST /api/v1/creative/concepts`)**:
```json
{
  "video_type": "explainer",
  "idea": "Explain how urban vertical farms save water compared to traditional farming.",
  "target_audience": "Sustainability-minded city residents",
  "desired_duration_seconds": 45
}
```

**Response (`200 OK`, truncated)**:
```json
{
  "concepts": [
    {
      "id": "concept_1",
      "title": "Story-First Explainer",
      "core_idea": "Ground Explain how urban vertical farms save water compared to traditional farming. in a relatable human moment before revealing the central insight.",
      "suggested_duration_seconds": 45
    },
    { "id": "concept_2", "title": "Visual Metaphor & Kinetic Rhythm" },
    { "id": "concept_3", "title": "Documentary Micro-Breakdown" }
  ],
  "recommended_concept_id": "concept_1",
  "provider_name": "mock",
  "model_name": "mock-creative-v1",
  "is_mock": true
}
```

## License

Released under the [MIT License](LICENSE).