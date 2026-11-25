
"""
VOXERA - Word Error Rate Engine
================================

Calculates:
- Substitutions
- Deletions
- Insertions
- Word Error Rate
"""

import re
from dataclasses import dataclass


def normalize_text(text: str) -> str:
    """Normalize text before comparing transcripts."""

    text = text.lower().strip()

    # Normalize hyphenated expressions.
    text = text.replace("-", " ")

    # Remove punctuation while preserving alphanumeric characters.
    text = re.sub(r"[^\w\s]", "", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text)

    return text


def tokenize(text: str) -> list[str]:
    """Convert normalized text into words."""

    normalized = normalize_text(text)

    return normalized.split() if normalized else []


@dataclass
class WERResult:
    substitutions: int
    deletions: int
    insertions: int
    reference_words: int
    edit_distance: int
    wer: float


def edit_distance(
    reference: list[str],
    hypothesis: list[str],
) -> tuple[int, int, int, int]:
    """
    Calculate minimum edit distance using dynamic programming.

    Returns:
        distance, substitutions, deletions, insertions
    """

    n = len(reference)
    m = len(hypothesis)

    # Each cell stores:
    # (total_cost, substitutions, deletions, insertions)

    dp = [[None] * (m + 1) for _ in range(n + 1)]

    dp[0][0] = (0, 0, 0, 0)

    for i in range(1, n + 1):
        dp[i][0] = (i, 0, i, 0)

    for j in range(1, m + 1):
        dp[0][j] = (j, 0, 0, j)

    for i in range(1, n + 1):
        for j in range(1, m + 1):

            if reference[i - 1] == hypothesis[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                continue

            previous = dp[i - 1][j - 1]

            substitution = (
                previous[0] + 1,
                previous[1] + 1,
                previous[2],
                previous[3],
            )

            previous = dp[i - 1][j]

            deletion = (
                previous[0] + 1,
                previous[1],
                previous[2] + 1,
                previous[3],
            )

            previous = dp[i][j - 1]

            insertion = (
                previous[0] + 1,
                previous[1],
                previous[2],
                previous[3] + 1,
            )

            dp[i][j] = min(
                substitution,
                deletion,
                insertion,
                key=lambda item: item[0],
            )

    return dp[n][m]


def calculate_wer(
    reference_text: str,
    hypothesis_text: str,
) -> WERResult:
    """Calculate WER between reference and hypothesis."""

    reference = tokenize(reference_text)
    hypothesis = tokenize(hypothesis_text)

    if not reference:
        raise ValueError(
            "Reference transcript cannot be empty."
        )

    distance, substitutions, deletions, insertions = (
        edit_distance(reference, hypothesis)
    )

    wer = distance / len(reference)

    return WERResult(
        substitutions=substitutions,
        deletions=deletions,
        insertions=insertions,
        reference_words=len(reference),
        edit_distance=distance,
        wer=wer,
    )
