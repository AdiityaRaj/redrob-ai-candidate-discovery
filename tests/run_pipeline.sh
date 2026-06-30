#!/usr/bin/env bash

set -euo pipefail

echo "=============================================="
echo " Redrob AI Candidate Discovery Pipeline"
echo "=============================================="

echo ""
echo "[1/3] Running ranking pipeline..."

python main_cli.py \
    --jd ./data/raw/job_description.docx \
    --candidates ./data/raw/candidates.jsonl \
    --out ./submission.csv

echo ""
echo "[2/3] Validating submission..."

python validate_submission.py submission.csv

echo ""
echo "[3/3] Completed."

echo ""
echo "Generated file:"
echo "submission.csv"