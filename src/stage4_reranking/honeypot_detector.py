import datetime
from typing import Dict, Any, Tuple
from src.utils.logger import logger

class HoneypotTrapDetector:
    """Detects and disqualifies impossible/fake candidate data layers (Honeypot Traps) locally on CPU."""

    def __init__(self):
        self.current_year = datetime.datetime.now().year

    def inspect_candidate(self, candidate_record: Dict[str, Any]) -> Tuple[bool, str]:
        """Scans candidate telemetry charts for chronological or platform logic impossibilities."""
        profile = candidate_record.get("profile", {})
        career_history = candidate_record.get("career_history", [])
        skills = candidate_record.get("skills", [])
        
        c_id = candidate_record.get("candidate_id", "UNKNOWN")
        total_exp_years = profile.get("years_of_experience", 0)

        # Trap 1: Chronological Impossibility (Future dates or impossible timelines)
        for job in career_history:
            start_date = job.get("start_date", "")
            end_date = job.get("end_date", "")
            
            if start_date:
                try:
                    start_year = int(start_date.split("-")[0])
                    if start_year > self.current_year:
                        logger.warning(f"🪤 Honeypot Caught [ID: {c_id}]: Future employment start year ({start_year}) discovered.")
                        return True, "Disqualified: Paradoxical employment history dates (Future Start Date)."
                except (ValueError, IndexError):
                    pass
            
            if start_date and end_date and end_date.lower() != "present":
                try:
                    start_year = int(start_date.split("-")[0])
                    end_year = int(end_date.split("-")[0])
                    if start_year > end_year:
                        logger.warning(f"🪤 Honeypot Caught [ID: {c_id}]: Job ends before it starts ({start_year} -> {end_year}).")
                        return True, "Disqualified: Career timeline inversion detected."
                except (ValueError, IndexError):
                    pass

        # Trap 2: Platform Fraud Signatures (Expert claim with 0 months real experience)
        expert_unearned_count = 0
        for skill in skills:
            proficiency = skill.get("proficiency", "").lower()
            duration = skill.get("duration_months", 0)
            if proficiency == "expert" and duration == 0:
                expert_unearned_count += 1

        if expert_unearned_count >= 5:
            logger.warning(f"🪤 Honeypot Caught [ID: {c_id}]: {expert_unearned_count} expert claims with exactly 0 months of background experience.")
            return True, f"Disqualified: Fabricated competencies profile ({expert_unearned_count} unearned experts)."

        # Trap 3: Experience vs Tenure Cap Mismatch
        aggregated_job_months = sum([job.get("tenure_months", 0) for job in career_history if job.get("tenure_months")])
        calculated_years = aggregated_job_months / 12.0
        if total_exp_years > calculated_years + 7.0: # Generous buffer, if it exceeds, it's artificially padded fluff
            logger.warning(f"🪤 Honeypot Caught [ID: {c_id}]: Declared {total_exp_years} yrs exp, but breakdown only supports {calculated_years:.1f} yrs.")
            return True, "Disqualified: Statistical inflation of experience bounds."

        return False, "Clear"
