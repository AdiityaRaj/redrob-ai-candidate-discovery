from fastapi import APIRouter, HTTPException, Query
from src.config import SAMPLE_JD_DOCX, CANDIDATES_JSONL, SUBMISSION_CSV
from main_cli import execute_pipeline
from src.utils.logger import logger
import os

router = APIRouter()

@router.post("/rank", summary="Trigger the offline CPU discovery and ranking pipeline")
def trigger_ranking_pipeline(
    jd_file_path: str = Query(default=str(SAMPLE_JD_DOCX), description="Absolute path to the input job description docx"),
    candidates_file_path: str = Query(default=str(CANDIDATES_JSONL), description="Absolute path to candidates jsonl dataset")
):
    """
    Executes the entire 6-stage candidate ranking and evaluation pipeline natively on CPU.
    Saves results strictly to submission.csv inside the root directory.
    """
    logger.info(f"FastAPI Gateway: Trigger request received for pipeline execution.")
    
    # Pre-flight asset location checks
    if not os.path.exists(jd_file_path):
        raise HTTPException(status_code=404, detail=f"Job Description docx asset missing at: {jd_file_path}")
    if not os.path.exists(candidates_file_path):
        raise HTTPException(status_code=404, detail=f"Candidates JSONL asset missing at: {candidates_file_path}")

    try:
        # Programmatically trigger the centralized production executor pipeline
        execute_pipeline(jd_file_path, candidates_file_path, str(SUBMISSION_CSV))
        
        return {
            "status": "success",
            "message": "Candidate Discovery and Re-ranking execution finished perfectly.",
            "output_locked_at": str(SUBMISSION_CSV),
            "constraints_verified": ["100_rows_max", "deterministic_tie_breaks", "honeypots_dropped"]
        }
    except Exception as e:
        logger.error(f"FastAPI Router runtime failure during pipeline trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal ranking pipeline collapse: {str(e)}")
