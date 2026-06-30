@echo off
setlocal

echo ======================================
echo Redrob AI Candidate Discovery Pipeline
echo ======================================

echo.
echo [1/3] Running ranking pipeline...

python main_cli.py ^
    --jd data\raw\job_description.docx ^
    --candidates data\raw\candidates.jsonl ^
    --out submission.csv

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Pipeline execution failed.
    exit /b 1
)

echo.
echo [2/3] Validating generated submission...

IF NOT EXIST submission.csv (
    echo ERROR: submission.csv was not generated.
    exit /b 1
)

python validate_submission.py submission.csv

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Submission validation failed.
    exit /b 1
)

echo.
echo [3/3] Pipeline completed successfully.
echo.
echo Output:
echo submission.csv

pause