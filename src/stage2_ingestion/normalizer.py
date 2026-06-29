import re
from typing import Dict, Any, List
from src.utils.logger import logger

class CandidateDataNormalizer:
    """Pre-processes and normalizes streaming noisy raw resume structures securely on CPU."""

    def __init__(self):
        # Map abbreviations to uniform naming convention arrays for proper dense matching
        self.title_mapping = {
            r"\bsr\b\.?": "senior",
            r"\bjr\b\.?": "junior",
            r"\bswe\b": "software engineer",
            r"\bdev\b": "developer",
            r"\bqa\b": "quality assurance"
        }

    def clean_text(self, text: str) -> str:
        """Strips punctuation noise, standardizes whitespace architectures and lowers case."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s\.\-\+#]', ' ', text) # Retains C++, C#, .NET formats safely
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def standardize_title(self, title: str) -> str:
        """Transforms inconsistent title variants into enterprise unified vocabulary strings."""
        cleaned_title = self.clean_text(title)
        for pattern, replacement in self.title_mapping.items():
            cleaned_title = re.sub(pattern, replacement, cleaned_title)
        return cleaned_title

    def create_searchable_chunk(self, candidate_record: Dict[str, Any]) -> str:
        """Flattens schema objects into hyper-focused semantic content documents for fast embedding."""
        profile = candidate_record.get("profile", {})
        skills = candidate_record.get("skills", [])
        career_history = candidate_record.get("career_history", [])

        # Process metadata contextually
        standard_title = self.standardize_title(profile.get("current_title", ""))
        skills_list = [s.get("name", "").lower() for s in skills if s.get("name")]
        
        experience_summary = []
        for job in career_history[:3]: # Focus heavily on recent 3 roles for optimal noise containment
            j_title = self.standardize_title(job.get("job_title", ""))
            j_desc = self.clean_text(job.get("description", ""))
            experience_summary.append(f"role: {j_title}. summary: {j_desc}")

        # Assemble unified sequence document target structure
        chunk_components = [
            f"current title: {standard_title}.",
            f"skills engineering footprint: {', '.join(skills_list)}.",
            f"historical career telemetry: {' | '.join(experience_summary)}"
        ]
        
        return " ".join(chunk_components)
