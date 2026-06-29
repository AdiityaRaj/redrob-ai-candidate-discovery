from typing import Dict, Any, Tuple
from src.utils.logger import logger

class HiddenTalentEngine:
    """Calculates mathematical underdog ranking scores bypassing format fluffs via platform telemetry vectors."""

    @staticmethod
    def evaluate_underdog_index(candidate_record: Dict[str, Any]) -> Tuple[float, str]:
        """Executes full formula matrix resolution for finding unpolished technical gems."""
        signals = candidate_record.get("redrob_signals", {})
        
        # 1. Metric A: Skill Consistency Index (Platform verified assessments vs unverified claims)
        assessment_scores = signals.get("skill_assessment_scores", {})
        if assessment_scores:
            avg_assessment = sum(assessment_scores.values()) / len(assessment_scores)
        else:
            avg_assessment = 50.0  # Baseline normalization floor standard
            
        profile_completeness = signals.get("profile_completeness_score", 100)
        # Inverse multiplier: If profile completeness is low but assessment scores are stellar -> High Underdog Factor!
        skill_consistency = (avg_assessment / 100.0) * (1.0 + (1.0 - (profile_completeness / 100.0)) * 0.3)

        # 2. Metric B: Career Velocity Vector (GitHub commits momentum vs profile view ratios)
        github_score = signals.get("github_activity_score", 0)
        github_modifier = github_score / 100.0 if github_score > -1 else 0.4 # Fair default baseline if github unlinked
        
        views = signals.get("profile_views_received_30d", 0)
        saves = signals.get("saved_by_recruiters_30d", 0)
        recruiter_pull_ratio = (saves / views) if views > 0 else 0.0
        
        career_velocity = (github_modifier * 0.6) + (min(recruiter_pull_ratio, 1.0) * 0.4)

        # 3. Metric C: Resume Formatting Penalty Counter-Inversion
        resume_formatting_score = profile_completeness / 100.0
        inverse_formatting_weight = 1.0 - (resume_formatting_score * 0.25)

        # Executing Final Combined Mathematical Architecture Formula
        hidden_talent_score = (skill_consistency * 0.45 + career_velocity * 0.35 + inverse_formatting_weight * 0.20) * 100.0
        hidden_talent_score = max(0.0, min(100.0, hidden_talent_score))

        # Categorization classification mapping bounds
        if hidden_talent_score >= 75.0:
            classification = "Underdog Detection Factor: Critical High (🔥 Hidden Gem)"
        elif hidden_talent_score >= 50.0:
            classification = "Underdog Detection Factor: Moderate Potential"
        else:
            classification = "Underdog Detection Factor: Standard Standard"

        return round(hidden_talent_score, 4), classification
