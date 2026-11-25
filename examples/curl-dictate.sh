#!/usr/bin/env bash
set -euo pipefail
curl -X POST "http://127.0.0.1:8000/api/v1/dictate" \
  -F "file=@sample.wav" \
  -F "language_code=en-IN"
