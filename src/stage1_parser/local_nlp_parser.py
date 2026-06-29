import os
import re
from typing import Dict, Any, List
from docx import Document
from src.utils.logger import logger
from src.config import SAMPLE_JD_DOCX

class LocalNLPJDParser:
    """Extracts job intelligence using rule-based parsing matching constraints safely without internet."""
    
    def __init__(self):
        # Multi-layered key mapping arrays for safe matching without cloud models
        self.experience_pattern = re.compile(r"(\d+)\s*(?:to|-|\+)?\s*(\d+)?\s*(?:years|yrs|year)", re.IGNORECASE)
        self.common_tech_stack = [
            "python", "java", "javascript", "typescript", "c++", "go", "rust", "ruby", "php",
            "aws", "azure", "gcp", "docker", "kubernetes", "fastapi", "django", "flask", 
            "react", "angular", "vue", "nodejs", "postgresql", "mysql", "redis", "mongodb",
            "spark", "hadoop", "tensorflow", "pytorch", "scikit-learn", "lightgbm", "qdrant"
        ]

    def _read_docx(self, file_path: str) -> str:
        """Safely extracts text strings out of local docx binaries."""
        if not os.path.exists(file_path):
            logger.error(f"Target JD file missing at path: {file_path}")
            raise FileNotFoundError(f"JD File not found: {file_path}")
        
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)

    def parse_job_description(self, file_path: str = str(SAMPLE_JD_DOCX)) -> Dict[str, Any]:
        """Parses raw text and extracts experience bounds and critical technical stacks."""
        logger.info("Initializing Local NLP Job Description Parsing Engine...")
        try:
            raw_text = self._read_docx(file_path)
            clean_text = raw_text.lower()
        except Exception as e:
            logger.critical(f"Failed to read input JD document: {str(e)}")
            return self._get_fallback_schema()

        # 1. Experience extraction via regex pattern boundaries
        min_years = 0
        max_years = 15 # Standard default fallback ceiling bound
        exp_match = self.experience_pattern.search(clean_text)
        if exp_match:
            try:
                groups = exp_match.groups()
                min_years = int(groups[0])
                if groups[1]:
                    max_years = int(groups[1])
                else:
                    max_years = min_years + 5 # Dynamic window scaling
            except (ValueError, TypeError):
                pass

        # 2. Extract technical stack matches from ground truth domain inventory
        must_have = []
        nice_to_have = []
        
        for tech in self.common_tech_stack:
            # Word boundary matching protects tokens (e.g., matching 'go' vs 'google')
            if re.search(r'\b' + re.escape(tech) + r'\b', clean_text):
                # Simple weight mapping heuristic: if it appears multiple times or high up, it's Must Have
                occurrences = len(re.findall(r'\b' + re.escape(tech) + r'\b', clean_text))
                if occurrences >= 2:
                    must_have.append(tech)
                else:
                    nice_to_have.append(tech)

        parsed_payload = {
            "min_experience": min_years,
            "max_experience": max_years,
            "must_have_skills": must_have if must_have else ["software engineering"],
            "nice_to_have_skills": nice_to_have,
            "raw_text_length": len(raw_text)
        }
        
        logger.info(f"JD Parsing Successful! Exp Range: {min_years}-{max_years} Yrs. Must-Haves: {must_have}")
        return parsed_payload

    def _get_fallback_schema(self) -> Dict[str, Any]:
        """Ensures system robustness even if document read pipeline fails completely."""
        return {
            "min_experience": 0,
            "max_experience": 10,
            "must_have_skills": ["python"],
            "nice_to_have_skills": [],
            "raw_text_length": 0
        }
