# Test & Reproducibility Scripts

This directory contains helper scripts to reproduce the complete Redrob AI Candidate Discovery & Ranking Engine pipeline on different operating systems.

## Files

- `run_pipeline.sh` — Linux/macOS execution script
- `run_pipeline.bat` — Windows execution script

Both scripts perform the following steps:

1. Execute the complete offline ranking pipeline.
2. Generate `submission.csv`.
3. Validate the generated submission using `validate_submission.py`.
4. Exit with a non-zero status if any step fails.

## Manual Reproduction

The same pipeline can also be reproduced directly from the repository root:

```bash
python main_cli.py \
    --jd ./data/raw/job_description.docx \
    --candidates ./data/raw/candidates.jsonl \
    --out ./submission.csv
```

## Notes

- Runs completely offline (no external APIs or network access).
- CPU-only execution.
- Produces a deterministic `submission.csv`.
- Compatible with the hackathon reproducibility requirements.