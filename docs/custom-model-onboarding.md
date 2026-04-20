# Custom Model Onboarding

## Supported provider styles (initial)
- OpenAI-compatible HTTP API
- Self-hosted adapter endpoints

## Onboarding steps
1. Register provider endpoint and auth mode
2. Register one or more models with capabilities
3. Set routing policy weight and fallback model
4. Validate with a smoke chat request
5. Monitor latency/error telemetry

## Required model metadata
- `model_id`
- Capabilities: `chat`, `code_completion`, `tool_calling`
- Context window
- Cost/latency class
- Safety tier
