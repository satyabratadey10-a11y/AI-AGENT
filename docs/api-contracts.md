# API Contracts (Draft)

## Health
- `GET /health` -> service status and timestamp

## Projects
- `GET /v1/projects`
- `POST /v1/projects` `{ name, template }`

## Workspaces
- `GET /v1/workspaces`
- `POST /v1/workspaces` `{ project_id, branch }`

## Model Gateway
- `GET /v1/models`
- `POST /v1/models/providers` register provider endpoint + auth mode
- `POST /v1/models` register model capabilities

## AI Chat
- `POST /v1/chat/completions`
  - Input: `messages`, `intent`, `preferred_model`, `project_id`, `open_files`
  - Output: `model`, `content`, `usage`, `latency_ms`

## Realtime (Planned)
- `GET /v1/realtime/session/{workspace_id}` (websocket)
  - terminal output events
  - file change events
  - streaming AI chunks
