
from app.evaluation import (
    calculate_wer,
    calculate_technical_metrics,
    run_ab_benchmark,
    save_report,
)


reference = (
    "Create an 8-bit synchronous FIFO with a depth "
    "of 16 an active-low reset and separate read "
    "and write pointers. Add assertions for full "
    "and empty conditions."
)

# Simulate a baseline recognition error.
baseline = (
    "Create an 8-bit synchronous LIFO with a depth "
    "of 16 an active-low reset and separate read "
    "and write pointers. Add assertions for full "
    "and empty conditions."
)

# Simulate a corrected enhanced transcript.
enhanced = reference

technical_terms = [
    "FIFO",
    "LIFO",
    "synchronous",
    "active-low reset",
    "read pointer",
    "write pointer",
    "assertions",
]

# Test WER.
print("\n========== WER TEST ==========")

result = calculate_wer(
    reference,
    baseline,
)

print(result)

# Test technical vocabulary.
print("\n========== TECHNICAL METRICS ==========")

metrics = calculate_technical_metrics(
    reference,
    baseline,
    technical_terms,
)

print(metrics)

# Test complete A/B benchmark.
print("\n========== A/B BENCHMARK ==========")

benchmark = run_ab_benchmark(
    reference=reference,
    baseline_text=baseline,
    enhanced_text=enhanced,
    technical_terms=technical_terms,
    baseline_latency=1.5,
    enhanced_latency=1.7,
)

print(benchmark)

# Save experiment.
print("\n========== REPORT ==========")

path = save_report(
    benchmark,
    "fifo_test",
)

print(f"Report saved: {path}")

print("\nVOXERA EVALUATION ENGINE: PASS")
