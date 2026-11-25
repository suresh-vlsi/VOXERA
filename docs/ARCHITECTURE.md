# VOXERA architecture — v0.1

## Design principles

1. Provider credentials and audio-provider calls stay on the backend.
2. Speech providers are accessed through adapters, not directly from routes or UI components.
3. Raw transcript and edited dictation remain separate data fields.
4. A degraded provider response is visible and never silently represented as a successful cleanup.
5. Tool execution and agent actions will require explicit policy checks and user approval.
6. Audio retention is off by default; this starter processes bytes in memory and does not persist recordings.

## Milestone 1 request flow

Browser upload → FastAPI validation → Sarvam provider adapter → normalized response → browser transcript panels.

## Planned provider interface

Future adapters should implement a common `transcribe()` contract so Sarvam can coexist with other hosted or local ASR providers.

## Security work before production

- Authentication, per-user quotas and rate limiting
- Malware/content scanning where appropriate
- Strict upload limits and MIME/signature validation
- Structured logging with audio and secrets excluded
- Privacy controls and explicit retention settings
- CORS restricted to deployed frontend origins
- Provider timeout/retry policy and request IDs
