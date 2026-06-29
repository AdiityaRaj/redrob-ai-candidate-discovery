import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CANDIDATES_JSONL = RAW_DATA_DIR / "candidates.jsonl"
SAMPLE_JD_DOCX = RAW_DATA_DIR / "job_description.docx"
SUBMISSION_CSV = BASE_DIR / "submission.csv"

# Storage Settings
QDRANT_STORAGE_PATH = str(PROCESSED_DATA_DIR / "qdrant_local_db")
COLLECTION_NAME = "redrob_candidates"

# Model Configurations (Network-Free / CPU Optimized)
# FastEmbed handles downloading on first init locally, then locks offline
DENSE_MODEL_NAME = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"

# Ensure all system directories exist automatically on bootup
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
