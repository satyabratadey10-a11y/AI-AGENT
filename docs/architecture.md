# Architecture Overview

## High-level components
1. **Android Client**
   - Native Kotlin + Compose
   - Offline-tolerant cache for workspace/session metadata
   - Realtime stream consumer for terminal/log/chat updates

2. **Control Plane (FastAPI)**
   - Auth/session APIs
   - Projects/workspaces metadata APIs
   - AI orchestration endpoint
   - Telemetry/event pipeline

3. **Execution Runtime (Planned Integration)**
   - Isolated containerized sandbox workers
   - Command execution + log streaming
   - Secret injection policy controls

4. **Model Gateway**
   - Provider registry (self-hosted + third-party)
   - Model capability metadata
   - Routing policy (latency/cost/fallback/safety)

## Data Flow (AI request)
- Android sends chat request with model preference + context
- Control plane enriches context through context pipeline
- Router selects model based on policy + capabilities
- Provider adapter executes inference
- Response + telemetry returned/recorded

## Security boundaries
- Execution sandbox network and filesystem isolation
- Secret redaction before logs and model prompts
- Provider access controls scoped by org/account
