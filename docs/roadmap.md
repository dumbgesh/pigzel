# Development Roadmap

Implementation is divided into six incremental milestones. Each milestone delivers testable, schema-validated functionality without premature infrastructure complexity.

---

## Milestone 1 — Project Foundation & Technical Specification *(Completed)*
- [x] Repository initialization and Git setup (`main` branch, `.gitignore`).
- [x] Modular backend package structure (`backend/app/...`).
- [x] Baseline `pyproject.toml`, `.env.example`, `LICENSE`, and `README.md`.
- [x] Finalized component architecture and boundaries ([architecture.md](architecture.md)).
- [x] End-to-end workflow lifecycle, approval gates, failure/retry, and version semantics ([workflow.md](workflow.md)).
- [x] Core Pydantic-aligned entity contracts ([data-contracts.md](data-contracts.md)).
- [x] Stage 1 implementation specification ([stage-1-creative-intelligence.md](stage-1-creative-intelligence.md)).
- [x] Architectural Decision Records ([decisions.md](decisions.md)).

## Milestone 2 — Creative Intelligence (Stage 1) *(In Progress — Core Agent & API Complete)*
- [x] Core configuration (`app/core/config.py`, `logging.py`, `exceptions.py`) and Pydantic v2 schemas (`app/schemas/creative.py`) for `CreativeBrief`, `CreativeConcept`, `CreativeDirection`, and `CreativeIntelligenceResult`.
- [x] Minimal `LLMProvider` protocol (`app/model_gateway/llm/base.py`), `MockLLMProvider` (`mock_provider.py`), and `get_llm_provider` factory (`factory.py`).
- [x] Brief normalization (`app/ingestion/brief_normalizer.py`).
- [x] **Creative Intelligence Agent (`app/agents/creative/`)**: generates 3 distinct concepts and 1 recommended direction, enforces schema validation with bounded retries, and separates prompt templates from agent logic.
- [x] FastAPI v1 endpoints (`GET /api/v1/health`, `POST /api/v1/creative/concepts`) and `pytest` suite (23 tests passing).
- [ ] OpenAI-compatible `httpx` LLM adapter for hosted open-weight / local inference.
- [ ] Lightweight `Project`, `ProjectVersion`, and `Approval` Gate 1 persistence (`app/storage`) and orchestrator revision loop (`app/orchestrator`).

## Milestone 3 — Visual Planning (Stage 2)
- Schemas for `Storyboard`, `Scene`, and Visual Bible.
- Image provider protocol in `app/model_gateway/image`.
- **Storyboard Director Agent (`app/agents/storyboard`)**:
  - Convert approved `CreativeDirection` into ordered `Scene` specs.
  - Maintain Visual Bible consistency and generate optional reference images.
- Approval Gate 2 and scene-editing endpoints + tests.

## Milestone 4 — Video Production & Assembly (Stage 3)
- Video and audio provider protocols in `app/model_gateway/video` and `app/model_gateway/audio`.
- **Production Planner Agent (`app/agents/production`)**:
  - Plan and execute per-scene `GenerationJob`s and `GeneratedAsset`s.
  - Support independent scene-level regeneration.
- Media assembly (`app/production`) integrating FFmpeg for clip concatenation, audio mixing, and export.

## Milestone 5 — Orchestration, Persistence & Integration
- Harden `Workflow Orchestrator` (`app/orchestrator`) with async job execution, failure recovery, and full traceability.
- Introduce PostgreSQL, Redis job queuing, and S3-compatible asset storage (`app/storage`) as justified by multi-user/async workloads.
- End-to-end integration tests and Docker setup.

## Milestone 6 — Frontend & Release
- Next.js + TypeScript web application in `frontend/`.
- Simple Mode and Advanced Mode UIs with interactive approval gates, storyboard editor, and scene regeneration controls.
- Example projects in `examples/` and public v0.1 release preparation.
