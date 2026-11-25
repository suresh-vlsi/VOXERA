
"""
VOXERA - A/B Benchmark Engine
==============================

Compares transcription with vocabulary disabled
against transcription with vocabulary enabled.
"""

from dataclasses import asdict

from app.evaluation.wer import calculate_wer
from app.evaluation.metrics import calculate_technical_metrics


def evaluate_transcript(
    reference: str,
    hypothesis: str,
    technical_terms: list[str],
    latency_seconds: float | None = None,
) -> dict:
    """Evaluate one transcription."""

    wer_result = calculate_wer(
        reference,
        hypothesis,
    )

    technical_result = calculate_technical_metrics(
        reference,
        hypothesis,
        technical_terms,
    )

    return {
        "wer": asdict(wer_result),
        "technical_metrics": asdict(technical_result),
        "latency_seconds": latency_seconds,
        "hypothesis": hypothesis,
    }


def run_ab_benchmark(
    reference: str,
    baseline_text: str,
    enhanced_text: str,
    technical_terms: list[str],
    baseline_latency: float | None = None,
    enhanced_latency: float | None = None,
) -> dict:
    """
    Run a controlled A/B transcription comparison.
    """

    baseline = evaluate_transcript(
        reference=reference,
        hypothesis=baseline_text,
        technical_terms=technical_terms,
        latency_seconds=baseline_latency,
    )

    enhanced = evaluate_transcript(
        reference=reference,
        hypothesis=enhanced_text,
        technical_terms=technical_terms,
        latency_seconds=enhanced_latency,
    )

    baseline_wer = baseline["wer"]["wer"]
    enhanced_wer = enhanced["wer"]["wer"]

    baseline_recall = (
        baseline["technical_metrics"]["recall"]
    )

    enhanced_recall = (
        enhanced["technical_metrics"]["recall"]
    )

    return {
        "experiment": "VOXERA Vocabulary A/B Test",

        "baseline": baseline,

        "enhanced": enhanced,

        "comparison": {
            "wer_improvement": (
                baseline_wer - enhanced_wer
            ),

            "technical_recall_improvement": (
                enhanced_recall - baseline_recall
            ),

            "better_wer": (
                "enhanced"
                if enhanced_wer < baseline_wer
                else "baseline"
                if baseline_wer < enhanced_wer
                else "tie"
            ),

            "better_technical_recall": (
                "enhanced"
                if enhanced_recall > baseline_recall
                else "baseline"
                if baseline_recall > enhanced_recall
                else "tie"
            ),
        },
    }
