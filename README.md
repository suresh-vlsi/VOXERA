# VOXERA

**Voice Intelligence Platform** — an independent, open-source voice-first AI application.

> Listen. Understand. Reason. Execute.

## Current milestone

Milestone 1 establishes a secure Sarvam Dictate clip workflow:

- Upload an audio clip (up to 30 seconds for the clip endpoint).
- Return the edited text and raw transcript separately.
- Preserve corrections, degraded status, and usage metadata.
- Keep provider credentials on the server.

## Architecture

- `frontend/`: React + TypeScript client (starter scaffold)
- `backend/`: FastAPI service and provider adapter
- `docs/`: architecture and development notes
- `examples/`: API usage examples

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux / WSL: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
# Add SARVAM_API_KEY to .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API and `http://127.0.0.1:8000/` for the starter UI.

## Configuration

`SARVAM_API_KEY` is required. Never put it in frontend code or commit `.env`.

## Important behavior

Sarvam Dictate returns both `text` (finished dictation) and `transcript` (raw ASR transcript). VOXERA exposes both. If `degraded` is non-null, the finishing step did not complete; the UI must label the result accordingly rather than presenting it as a fully edited result.

The initial integration uses the official Python SDK version documented by Sarvam at project initialization: `sarvamai==0.1.49a1`. Pin and validate SDK upgrades deliberately.

## Roadmap

1. Clip dictation API and secure provider adapter
2. Browser recording and polished dictation workspace
3. Domain vocabulary and context profiles
4. Structured output with schema validation
5. Long-audio jobs
6. Server-proxied live WebSocket dictation
7. Provider abstraction and additional speech backends
8. Agent workflows with explicit user approval and audit logs


cat >> README.md <<'EOF'

---

## Production Deployment & Verification

**VOXERA v0.1.0 is deployed and publicly accessible.**

### Live Application

| Component | Deployment |
|---|---|
| Frontend | [VOXERA on Vercel](https://voxera-kappa.vercel.app/) |
| Backend API | [VOXERA on Render](https://voxera-gibk.onrender.com/) |
| API Documentation | [Swagger UI](https://voxera-gibk.onrender.com/docs) |
| Health Check | [Backend Health](https://voxera-gibk.onrender.com/health) |

### Deployment Architecture

```text
                User Browser
                     |
                     v
          Vercel - React + Vite
                     |
                HTTPS / CORS
                     |
                     v
          Render - FastAPI Backend
                     |
                     v
              Sarvam AI API
                     |
                     v
          Transcription Response
                     |
                     v
             VOXERA Web Interface
```

### Production Verification

The following checks have been performed against the deployed application:

| Test | Result |
|---|---|
| Frontend deployment on Vercel | Passed |
| Backend deployment on Render | Passed |
| Backend health endpoint | HTTP 200 |
| Swagger API documentation | HTTP 200 |
| CORS preflight request | HTTP 200 |
| Frontend-to-backend connectivity | Passed |
| Live microphone recording | Passed |
| Audio upload to backend | Passed |
| Sarvam transcription | Passed |
| Transcription displayed in frontend | Passed |
| Analytics API endpoints | Passed |

A live microphone recording was successfully processed through the production pipeline and returned a transcription.

### Current Deployment Notes

- Analytics endpoints are operational, but the production report collection is currently empty.
- Evaluation reports are stored using the backend filesystem. Persistent storage is not yet configured.
- Render free instances may spin down after inactivity, introducing cold-start delays.
- Engineering vocabulary recognition requires further controlled testing using technical speech samples.

---

EOF

## License

MIT (see `LICENSE`).
