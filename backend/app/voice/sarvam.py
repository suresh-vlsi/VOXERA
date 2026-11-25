
"""
VOXERA Sarvam Dictate Provider
==============================

Handles communication with Sarvam Dictate.

Responsibilities:
- Initialize the Sarvam SDK.
- Submit audio for transcription.
- Pass optional engineering vocabulary.
- Normalize provider responses.
"""

from typing import Any

from sarvamai import SarvamAI


class SarvamDictateProvider:
    """Adapter for the Sarvam Dictate speech recognition API."""

    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError(
                "SARVAM_API_KEY is not configured."
            )

        self.client = SarvamAI(
            api_subscription_key=api_key
        )

    def transcribe(
        self,
        audio_file,
        language_code: str = "unknown",
        vocabulary: list[dict[str, object]] | None = None,
    ) -> dict[str, Any]:
        """
        Transcribe audio using Sarvam Dictate.

        Args:
            audio_file: File-like audio object.
            language_code: Language identifier.
            vocabulary: Optional engineering vocabulary.

        Returns:
            Normalized transcription response.
        """

        request = {
            "file": audio_file,
            "language_code": language_code,
        }

        if vocabulary:
            request["vocabulary"] = vocabulary

        response = self.client.dictate.transcribe(
            **request
        )

        return {
            "text": getattr(response, "text", None),
            "transcript": getattr(
                response, "transcript", None
            ),
            "degraded": getattr(
                response, "degraded", None
            ),
            "corrections": getattr(
                response, "corrections", None
            ) or [],
            "usage": getattr(
                response, "usage", None
            ),
        }
