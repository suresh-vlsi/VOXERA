
"""
VOXERA API Routes
=================

Audio transcription API with:
- Sarvam Dictate integration
- Technical vocabulary selection
- Vocabulary ON/OFF experimentation
- Audio validation
- Asynchronous request handling
- Structured response metadata
"""

from io import BytesIO

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.encoders import jsonable_encoder
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.voice.sarvam import SarvamDictateProvider
from app.voice.vocabulary import (
    available_domains,
    build_sarvam_vocabulary,
)
from app.evaluation import (
    run_ab_benchmark,
    save_report,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["dictation"],
)


# =========================================================
# CONFIGURATION
# =========================================================

ALLOWED_SUFFIXES = {
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
    ".webm",
}

DEFAULT_VOCABULARY_DOMAINS = (
    "digital_design,verification"
)

MAX_VOCABULARY_TERMS = 100


# =========================================================
# DICTATION ENDPOINT
# =========================================================

@router.post(
    "/dictate",
    summary="Transcribe engineering audio",
    description=(
        "Transcribe audio using Sarvam Dictate with "
        "optional VOXERA technical vocabulary."
    ),
)
async def dictate(
    file: UploadFile = File(...),

    language_code: str = Form("auto"),

    vocabulary_domains: str = Form(
        DEFAULT_VOCABULARY_DOMAINS
    ),

    vocabulary_enabled: bool = Form(True),
):
    """
    Transcribe an uploaded audio recording.

    Parameters:
        file:
            Audio recording.

        language_code:
            Speech recognition language.

        vocabulary_domains:
            Comma-separated vocabulary domains.

        vocabulary_enabled:
            Enables or disables custom vocabulary.

    Returns:
        Transcript, corrections, usage and metadata.
    """

    settings = get_settings()

    try:

        # -------------------------------------------------
        # 1. VALIDATE FILE
        # -------------------------------------------------

        filename = file.filename or ""

        suffix = (
            "." + filename.rsplit(".", 1)[-1].lower()
            if "." in filename
            else ""
        )

        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(
                status_code=415,
                detail=(
                    "Unsupported audio format. "
                    "Use WAV, MP3, M4A, AAC, OGG, FLAC or WEBM."
                ),
            )

        # -------------------------------------------------
        # 2. READ AUDIO
        # -------------------------------------------------

        audio = await file.read()

        max_bytes = (
            settings.voxera_max_upload_mb
            * 1024
            * 1024
        )

        if not audio:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty.",
            )

        if len(audio) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Audio exceeds the configured "
                    f"{settings.voxera_max_upload_mb} MB limit."
                ),
            )

        # -------------------------------------------------
        # 3. PARSE VOCABULARY DOMAINS
        # -------------------------------------------------

        domains = [
            domain.strip()
            for domain in vocabulary_domains.split(",")
            if domain.strip()
        ]

        vocabulary = []

        selected_domains = []

        # -------------------------------------------------
        # 4. VOCABULARY ON/OFF CONTROL
        # -------------------------------------------------

        if vocabulary_enabled:

            if not domains:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "At least one vocabulary domain "
                        "is required when vocabulary is enabled."
                    ),
                )

            supported_domains = set(
                available_domains()
            )

            invalid_domains = [
                domain
                for domain in domains
                if domain not in supported_domains
            ]

            if invalid_domains:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Unsupported vocabulary domains.",
                        "invalid_domains": invalid_domains,
                        "available_domains": sorted(
                            supported_domains
                        ),
                    },
                )

            # Build selected vocabulary.
            vocabulary = build_sarvam_vocabulary(
                domains=domains,
                max_terms=MAX_VOCABULARY_TERMS,
            )

            selected_domains = domains

        # When disabled, vocabulary remains an empty list.
        # The Sarvam request will omit the vocabulary field.

        # -------------------------------------------------
        # 5. INITIALIZE PROVIDER
        # -------------------------------------------------

        provider = SarvamDictateProvider(
            settings.sarvam_api_key
        )

        # -------------------------------------------------
        # 6. PREPARE AUDIO STREAM
        # -------------------------------------------------

        audio_stream = BytesIO(audio)

        audio_stream.name = filename or "audio.wav"

        # -------------------------------------------------
        # 7. TRANSCRIBE AUDIO
        # -------------------------------------------------

        result = await run_in_threadpool(
            provider.transcribe,
            audio_stream,
            language_code,
            vocabulary if vocabulary_enabled else None,
        )

        # -------------------------------------------------
        # 8. BUILD RESPONSE
        # -------------------------------------------------

        response = {
            "provider": "sarvam",

            "result": result,

            "metadata": {
                "language_code": language_code,

                "vocabulary_enabled": vocabulary_enabled,

                "vocabulary_domains": selected_domains,

                "vocabulary_terms_used": len(vocabulary),

                "audio_filename": filename,

                "audio_size_bytes": len(audio),
            },
        }

        return jsonable_encoder(response)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        # Do not expose credentials or provider internals.
        raise HTTPException(
            status_code=502,
            detail=(
                "Dictation provider request failed. "
                "Check backend logs and API configuration."
            ),
        ) from exc

    finally:
        await file.close()


# =========================================================
# EVALUATION ENDPOINT
# =========================================================

@router.post(
    "/evaluate",
    summary="Evaluate transcription accuracy",
    description=(
        "Compare baseline and vocabulary-enhanced "
        "transcriptions against a reference transcript."
    ),
)
async def evaluate(
    reference: str = Form(...),

    baseline_text: str = Form(...),

    enhanced_text: str = Form(...),

    technical_terms: str = Form(...),

    baseline_latency: float | None = Form(None),

    enhanced_latency: float | None = Form(None),
):
    """Run a VOXERA transcription benchmark."""

    if not reference.strip():
        raise HTTPException(
            status_code=400,
            detail="Reference transcript cannot be empty.",
        )

    if not baseline_text.strip() or not enhanced_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Both transcripts are required.",
        )

    if (
        baseline_latency is not None
        and baseline_latency < 0
    ) or (
        enhanced_latency is not None
        and enhanced_latency < 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Latency cannot be negative.",
        )

    terms = [
        term.strip()
        for term in technical_terms.split(",")
        if term.strip()
    ]

    if not terms:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one technical term.",
        )

    try:
        benchmark = run_ab_benchmark(
            reference=reference,
            baseline_text=baseline_text,
            enhanced_text=enhanced_text,
            technical_terms=terms,
            baseline_latency=baseline_latency,
            enhanced_latency=enhanced_latency,
        )

        report_path = save_report(
            benchmark,
            "voxera_api_benchmark",
        )

        return jsonable_encoder({
            "status": "success",
            "benchmark": benchmark,
            "report": str(report_path),
        })

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Evaluation failed.",
        ) from exc
