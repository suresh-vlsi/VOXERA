
"""
VOXERA - Phrase-Aware Technical Vocabulary Evaluator
=====================================================

Features:
- Multi-word technical phrase matching
- Coordinated phrase normalization
- Technical aliases
- Repeated occurrence counting
- Occurrence-based precision, recall and F1
"""

import re
from dataclasses import dataclass, field

from app.evaluation.wer import normalize_text


# ---------------------------------------------------------
# COORDINATED ENGINEERING EXPRESSIONS
# ---------------------------------------------------------

COORDINATED_PHRASES = [
    (
        r"\bread and write pointers\b",
        "read pointer and write pointer",
    ),
    (
        r"\bfull and empty conditions\b",
        "full condition and empty condition",
    ),
    (
        r"\btransmit and receive signals\b",
        "transmit signal and receive signal",
    ),
    (
        r"\bread and write operations\b",
        "read operation and write operation",
    ),
]


# ---------------------------------------------------------
# TECHNICAL ALIASES
# ---------------------------------------------------------

DEFAULT_ALIASES = {
    "fifo": ["first in first out"],
    "lifo": ["last in first out"],
    "rtl": ["register transfer level"],
    "sva": ["systemverilog assertions"],
    "uart": ["universal asynchronous receiver transmitter"],
    "spi": ["serial peripheral interface"],
    "i2c": ["inter integrated circuit"],
    "mosfet": ["metal oxide semiconductor field effect transistor"],
}


@dataclass
class TechnicalMetrics:
    total_reference_terms: int
    recognized_terms: int
    missed_terms: list[str]
    extra_terms: list[str]
    precision: float
    recall: float
    f1_score: float

    total_hypothesis_terms: int = 0
    term_details: dict = field(default_factory=dict)


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def normalize_engineering_text(text: str) -> str:
    """Normalize technical speech before phrase matching."""

    normalized = normalize_text(text)

    for pattern, replacement in COORDINATED_PHRASES:
        normalized = re.sub(
            pattern,
            replacement,
            normalized,
        )

    return normalized


# ---------------------------------------------------------
# PHRASE MATCHING
# ---------------------------------------------------------

def count_phrase_occurrences(
    text: str,
    phrase: str,
) -> int:
    """Count complete, non-overlapping phrase occurrences."""

    normalized_text = normalize_engineering_text(text)
    normalized_phrase = normalize_engineering_text(phrase)

    if not normalized_phrase:
        return 0

    pattern = (
        r"(?<!\w)"
        + r"\s+".join(
            re.escape(token)
            for token in normalized_phrase.split()
        )
        + r"(?!\w)"
    )

    return len(
        re.findall(pattern, normalized_text)
    )


def get_term_aliases(
    term: str,
    aliases: dict[str, list[str]] | None = None,
) -> list[str]:
    """Return canonical term and its supported aliases."""

    custom_aliases = aliases or {}

    normalized_term = normalize_text(term)

    result = [
        term,
        *DEFAULT_ALIASES.get(normalized_term, []),
        *custom_aliases.get(term, []),
    ]

    # Remove duplicate variants.
    unique = {}

    for variant in result:
        normalized = normalize_text(variant)

        if normalized:
            unique.setdefault(normalized, variant)

    return list(unique.values())


# ---------------------------------------------------------
# TECHNICAL VOCABULARY EVALUATION
# ---------------------------------------------------------

def calculate_technical_metrics(
    reference_text: str,
    hypothesis_text: str,
    technical_terms: list[str],
    aliases: dict[str, list[str]] | None = None,
) -> TechnicalMetrics:
    """
    Evaluate technical-term recognition by occurrence.

    True positives:
        Correctly recognized term occurrences.

    False negatives:
        Reference occurrences that were missed.

    False positives:
        Additional recognized occurrences.
    """

    if not technical_terms:
        raise ValueError(
            "Provide at least one technical term."
        )

    reference_total = 0
    hypothesis_total = 0
    true_positive = 0

    missed = []
    extra = []
    details = {}

    for term in technical_terms:

        variants = get_term_aliases(
            term,
            aliases,
        )

        reference_count = max(
            count_phrase_occurrences(
                reference_text,
                variant,
            )
            for variant in variants
        )

        hypothesis_count = max(
            count_phrase_occurrences(
                hypothesis_text,
                variant,
            )
            for variant in variants
        )

        matched = min(
            reference_count,
            hypothesis_count,
        )

        missed_count = max(
            reference_count - hypothesis_count,
            0,
        )

        extra_count = max(
            hypothesis_count - reference_count,
            0,
        )

        reference_total += reference_count
        hypothesis_total += hypothesis_count
        true_positive += matched

        missed.extend(
            [term] * missed_count
        )

        extra.extend(
            [term] * extra_count
        )

        details[term] = {
            "reference_occurrences": reference_count,
            "hypothesis_occurrences": hypothesis_count,
            "matched_occurrences": matched,
            "missed_occurrences": missed_count,
            "extra_occurrences": extra_count,
        }

    false_positive = hypothesis_total - true_positive
    false_negative = reference_total - true_positive

    precision = (
        true_positive / hypothesis_total
        if hypothesis_total else 0.0
    )

    recall = (
        true_positive / reference_total
        if reference_total else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return TechnicalMetrics(
        total_reference_terms=reference_total,
        recognized_terms=true_positive,
        missed_terms=missed,
        extra_terms=extra,
        precision=precision,
        recall=recall,
        f1_score=f1,
        total_hypothesis_terms=hypothesis_total,
        term_details=details,
    )
