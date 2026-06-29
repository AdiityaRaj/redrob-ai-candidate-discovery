#!/usr/bin/env bash

set -euo pipefail

echo "=================================================="
echo " Redrob AI Candidate Discovery & Ranking Engine"
echo " Reproducibility Pipeline"
echo "=================================================="

echo ""
echo "[1/3] Running ranking pipeline..."
python main_cli.py

echo ""
echo "[2/3] Validating generated submission..."

if [ ! -f submission.csv ]; then
    echo "ERROR: submission.csv was not generated."
    exit 1
fi

python validate_submission.py submission.csv

echo ""
echo "[3/3] Pipeline completed successfully."

echo ""
echo "Submission file generated:"
echo "submission.csv"

echo ""
echo "All validation checks passed."