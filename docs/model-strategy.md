# Model Strategy

> **Status**: Guiding strategy. Specific model selections are intentionally deferred until each stage is implemented and benchmarked.

## Core Principles

1. **Open-Weight Models First**
   - Prefer open-weight models for transparency, reproducibility, cost control, and community self-hosting.
   - Ensure Pigzel does not lock users into a single proprietary ecosystem.

2. **Hosted Inference APIs as Primary Runtime**
   - Use hosted inference APIs for open-weight models as the default practical deployment path, avoiding heavy local GPU requirements for contributors and standard users.

3. **Optional Local Inference**
   - Support local inference endpoints (e.g., OpenAI-compatible local servers, ComfyUI/diffusers workers, or local audio runners) through the same gateway interfaces.

4. **Proprietary Fallbacks Where Justified**
   - Allow proprietary hosted APIs when an open-weight model cannot yet meet quality, consistency, or latency requirements for a specific capability.

5. **Model-Provider Independence**
   - Agents never call vendor SDKs directly. All inference goes through `backend/app/model_gateway`.

## Capability Separation

The Model Gateway separates inference into four independent capability interfaces:

| Capability | Responsibility | Examples of Use |
| :--- | :--- | :--- |
| **LLM** (`model_gateway/llm`) | Reasoning, structured JSON output, multimodal brief analysis | Stage 1 concepts, Stage 2 scene breakdown |
| **Image** (`model_gateway/image`) | Reference frames, character/environment sheets, keyframes | Stage 2 visual bible & keyframes |
| **Video** (`model_gateway/video`) | Text-to-video and image-to-video clip synthesis | Stage 3 scene clip generation |
| **Audio** (`model_gateway/audio`) | Speech/voiceover, sound effects, background music | Stage 3 audio tracks |

## Provider Abstraction Design

Each capability defines:
- A small, typed **provider interface** (protocol / abstract base class) accepting validated request models and returning validated response models.
- **Configuration-driven selection** via environment variables or project settings (no hardcoded keys or model IDs in business logic).
- **Normalized error handling** (rate limits, timeouts, transient failures) so the Orchestrator can retry or fall back cleanly.
