# Architectural Decisions (ADRs)

This log records key architectural decisions, their context, and rationale.

---

## ADR-001: Modular Three-Stage Pipeline with Human Approval Gates
- **Status**: Accepted
- **Context**: End-to-end "one-shot" video generation gives users little creative control and wastes compute when early narrative or visual assumptions are wrong.
- **Decision**: Split production into three explicit stages — Creative Intelligence, Visual Planning, and Video Production — separated by mandatory human approval gates.
- **Rationale**: Improves creative alignment, enables early course correction, and makes each stage independently testable and replaceable. Stages represent responsibilities, not a restriction to three AI models.

## ADR-002: Provider-Independent Model Gateway
- **Status**: Accepted
- **Context**: AI video, image, audio, and LLM ecosystems evolve rapidly, and contributors may prefer hosted open-weight APIs, local inference, or proprietary fallbacks.
- **Decision**: Route all AI calls through `backend/app/model_gateway` split by capability (`llm`, `image`, `video`, `audio`) rather than calling vendor SDKs inside agents.
- **Rationale**: Prevents vendor lock-in, simplifies testing with mock providers, and supports an open-weight-first strategy with optional local or proprietary backends.

## ADR-003: Schema-Validated Outputs with Pydantic v2
- **Status**: Accepted
- **Context**: Passing unstructured text between AI stages causes brittle downstream parsing and silent failures.
- **Decision**: Enforce strict Pydantic v2 schemas (`backend/app/schemas`) at every API boundary and between all agent stages.
- **Rationale**: Guarantees structural contracts, enables automatic validation/retry on malformed AI responses, and keeps stage interfaces explicit.

## ADR-004: Defer Database, Queue, and Frontend Infrastructure
- **Status**: Accepted
- **Context**: Setting up PostgreSQL, Redis, S3, Docker, and Next.js before the core AI pipeline and schemas exist slows iteration and adds premature complexity.
- **Decision**: Begin with Python 3.12+, FastAPI, Pydantic v2, HTTPX, and Pytest. Introduce database, queuing, object storage, and frontend in later milestones once data models and workflows are proven.
- **Rationale**: Keeps the foundation lean, avoids unnecessary dependencies, and accelerates delivery of Milestone 2 (Creative Intelligence).

## ADR-005: Scene-Level Regeneration and Versioned Outputs
- **Status**: Accepted
- **Context**: Regenerating an entire video when only one scene is flawed is slow and expensive.
- **Decision**: Model storyboards and production manifests as collections of independently addressable, versioned scenes.
- **Rationale**: Enables targeted scene regeneration, preserves unaffected clips, and provides clear version history and traceability.

## ADR-006: Local JSON and Filesystem Store for Early Milestones
- **Status**: Accepted
- **Context**: Milestone 2 (Creative Intelligence) requires persisting `Project`, `ProjectVersion`, and `Approval` records, but introducing PostgreSQL and S3 migrations before schemas stabilize adds unnecessary overhead.
- **Decision**: Implement a minimal `Storage` interface in `backend/app/storage` backed by a local filesystem JSON + asset store (plus an in-memory implementation for `pytest`), deferring PostgreSQL and S3-compatible storage to Milestone 5.
- **Rationale**: Keeps local development zero-config, isolates persistence behind a clean repository boundary, and avoids premature database coupling.

## ADR-007: Immutable Project Versions with Lineage
- **Status**: Accepted
- **Context**: Human revisions at approval gates, scene-level regenerations, and full-video regenerations all alter pipeline outputs.
- **Decision**: Treat `ProjectVersion` snapshots as immutable once they reach a gate or complete. Any revision or regeneration creates a new `ProjectVersion` referencing `parent_version_id`, while `Project.active_version_id` tracks the active version.
- **Rationale**: Prevents accidental loss of approved work, supports side-by-side comparison and rollback, and simplifies scene-level asset reuse.

## ADR-008: Minimal Custom Orchestrator and Provider Protocols
- **Status**: Accepted
- **Context**: Heavy AI agent frameworks (e.g., LangChain, CrewAI) introduce large dependency trees, opaque control flow, and abstractions that conflict with Pigzel's explicit state machine.
- **Decision**: Build a small, custom Python orchestrator and typed `typing.Protocol` provider interfaces using `httpx` and `pydantic` v2 directly.
- **Rationale**: Maximizes debuggability, keeps dependencies minimal, avoids framework lock-in, and gives full control over retries, approvals, and schema validation.

## ADR-009: Standardized Core Data Contracts Across Documentation and Code
- **Status**: Accepted
- **Context**: Early drafts used slightly varying names across documents (e.g., `ProjectBrief` vs `CreativeBrief`, `SceneSpec` vs `Scene`).
- **Decision**: Standardize all modules and documentation on the canonical entity set defined in [data-contracts.md](data-contracts.md): `Project`, `ProjectVersion`, `CreativeBrief`, `CreativeConcept`, `CreativeDirection`, `Storyboard`, `Scene`, `GenerationJob`, `GeneratedAsset`, and `Approval`.
- **Rationale**: Eliminates ambiguity between design docs, API schemas, and agent implementations.
