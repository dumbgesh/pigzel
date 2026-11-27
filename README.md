# PIGZEL

**An open-source, modular AI video production platform.**

Turn ideas into videos through a coordinated workflow of AI agents, creative planning and automated production.

> PIGZEL is currently under active development.

## Overview

PIGZEL aims to simplify video production by breaking it into three stages:

1. **Creative Intelligence** — Understands your idea and develops creative concepts.
2. **Storyboard Director** — Transforms the selected concept into a structured visual storyboard.
3. **Production Planner** — Coordinates media generation and assembles the final video.

Each stage includes human review and approval.

## Development Status

| Component | Status |
|---|---|
| Backend foundation | Implemented |
| Creative Intelligence | Partially implemented |
| Storyboard Director | Planned |
| Production Planner | Planned |
| Frontend | Planned |
| Media generation | Planned |

The current Creative Intelligence implementation uses a mock LLM provider for development and testing. Live AI model integration is not yet available.

## Technology

- **Backend:** Python, FastAPI, Pydantic
- **Frontend:** Next.js, TypeScript (planned)
- **Testing:** Pytest
- **Video processing:** FFmpeg (planned)

## Getting Started

### Requirements

- Python 3.12+

### Installation

```bash
git clone https://github.com/dumbgesh/pigzel.git
cd pigzel/backend

pip install -e ".[dev]"
```

### Run the backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

### Run tests

```bash
pytest -v
```

## Documentation

- [Architecture](docs/architecture.md)
- [Product Requirements](docs/product-requirements.md)
- [Data Contracts](docs/data-contracts.md)
- [Agent Specifications](docs/agent-specifications.md)
- [Development Roadmap](docs/roadmap.md)
- [Model Strategy](docs/model-strategy.md)
- [Workflow](docs/workflow.md)
- [Technical Decisions](docs/decisions.md)

## Contributing

PIGZEL is an open-source project under active development. Contributions, discussions and suggestions are welcome.

## License

[MIT License](LICENSE)