@echo off

echo ======================================
echo Redrob AI Ranking Pipeline
echo ======================================

python main_cli.py

IF NOT EXIST submission.csv (
    echo ERROR: submission.csv not generated.
    exit /b 1
)

python validate_submission.py submission.csv

echo.
echo Pipeline completed successfully.
pause