# Product Requirements (MVP)

## Goal
Deliver an Android-only AI coding workspace with Replit-like essentials and custom model support.

## MVP Features
- Project/workspace lifecycle (create/import/open/list)
- Editor-ready backend support for files and diagnostics integration
- Terminal/session log streaming hooks via realtime channels
- AI chat + code action intents (explain/generate/refactor/fix)
- Run/build orchestration API contracts
- Custom model provider registration and model selection

## Non-goals (v1)
- Web/iOS clients
- Full multiplayer collaboration
- Advanced deployment marketplace

## Acceptance Criteria
- Android app can authenticate and list/create projects
- Backend can register providers/models and route chat requests
- Chat endpoint returns deterministic response via pluggable adapters
- Documented API contracts for all MVP domains
- Basic telemetry and redaction hooks are active

## Success Metrics
- P95 AI first token latency target defined and tracked
- Project open success rate tracked
- Crash-free sessions tracked
- AI response quality feedback collection enabled
