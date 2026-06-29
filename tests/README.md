# Test & Reproducibility Scripts

This directory contains helper scripts to reproduce the Redrob AI Candidate Discovery & Ranking Engine pipeline on different operating systems.

## Files

- `run_pipeline.sh` – Linux/macOS execution script.
- `run_pipeline.bat` – Windows execution script.

Both scripts perform the following steps:

1. Execute the complete offline ranking pipeline (`main_cli.py`).
2. Generate `submission.csv`.
3. Run `validate_submission.py` to verify the output format.
4. Exit with a non-zero status if any step fails.

The project can also be reproduced directly using:

```bash
python main_cli.py
```

The pipeline is designed to run completely offline on CPU without requiring network access.