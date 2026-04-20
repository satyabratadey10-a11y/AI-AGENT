# AI-AGENT

Android-first AI coding workspace inspired by Replit, with custom AI model support through a provider-agnostic gateway.

## Repository layout

- `/android` – native Android application skeleton (Jetpack Compose)
- `/backend` – control plane API and model gateway (FastAPI)
- `/docs` – MVP scope, architecture, contracts, security, quality, roadmap

## Quick start

### Backend

```bash
cd /home/runner/work/AI-AGENT/AI-AGENT/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Backend tests

```bash
cd /home/runner/work/AI-AGENT/AI-AGENT/backend
pytest -q
```

## Current status

This repository now includes a production-oriented foundation for:

- MVP scope and acceptance criteria documentation
- Android app structure for phone/tablet UI evolution
- Control plane API skeleton (projects/workspaces/models/chat)
- Provider-agnostic model registration and routing abstractions
- Prompt/context pipeline and basic telemetry events
- Security and operational baseline documentation
