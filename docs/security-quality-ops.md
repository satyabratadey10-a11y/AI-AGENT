# Security, Quality, and Operations Baseline

## Security
- Sandbox isolation required for command execution workers
- Redaction pass for secrets in logs/prompt context
- Rate limits for AI and runtime endpoints
- Audit events for admin/model/project actions

## Quality Strategy
- Backend: unit + integration tests (pytest)
- Android: unit + UI test targets (planned)
- Runtime: sandbox validation suite (planned)
- SLOs: AI latency, project open success, run/build reliability

## Operations
- CI workflow for backend tests
- Staged environments: dev/staging/prod
- Feature flags for rollout
- Telemetry dashboards for adoption, reliability, cost
