
from app.evaluation.metrics import (
    calculate_technical_metrics,
    count_phrase_occurrences,
)


def test_coordinated_pointers():

    reference = "Use separate read and write pointers."

    hypothesis = "Use separate read pointer and write pointer."

    result = calculate_technical_metrics(
        reference,
        hypothesis,
        ["read pointer", "write pointer"],
    )

    assert result.total_reference_terms == 2
    assert result.recognized_terms == 2
    assert result.recall == 1.0

    print("Coordinated pointers: PASS")


def test_fifo_lifo():

    reference = "Create a FIFO with a depth of 16."

    hypothesis = "Create a LIFO with a depth of 16."

    result = calculate_technical_metrics(
        reference,
        hypothesis,
        ["FIFO", "LIFO"],
    )

    assert result.missed_terms == ["FIFO"]
    assert result.extra_terms == ["LIFO"]

    print("FIFO/LIFO detection: PASS")


def test_repeated_occurrences():

    reference = "FIFO FIFO FIFO"

    hypothesis = "FIFO FIFO"

    result = calculate_technical_metrics(
        reference,
        hypothesis,
        ["FIFO"],
    )

    assert result.total_reference_terms == 3
    assert result.total_hypothesis_terms == 2
    assert result.recognized_terms == 2
    assert result.recall == 2 / 3

    print("Repeated occurrences: PASS")


def test_technical_aliases():

    reference = "Use first in first out architecture."

    hypothesis = "Use FIFO architecture."

    result = calculate_technical_metrics(
        reference,
        hypothesis,
        ["FIFO"],
    )

    assert result.precision == 1.0
    assert result.recall == 1.0

    print("Technical aliases: PASS")


def test_word_boundaries():

    assert count_phrase_occurrences(
        "FIFO FIFOs AFIFO",
        "FIFO",
    ) == 1

    print("Word boundaries: PASS")


if __name__ == "__main__":

    test_coordinated_pointers()
    test_fifo_lifo()
    test_repeated_occurrences()
    test_technical_aliases()
    test_word_boundaries()

    print("\nALL PHRASE METRIC TESTS PASSED")
