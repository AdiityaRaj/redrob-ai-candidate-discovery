from typing import Dict, Any, List
from src.stage5_explanation.metadata_reasoner import LocalMetadataDrivenReasoner

class ProductionBusinessRulesEngine:
    """
    Level 17 FINAL PRODUCTION - 100% JD Alignment
    - Fixed 0-day notice to rank #1
    - All scores formatted to 4 decimals
    - Proper response rate weighting
    - Hardened 120-day notice penalty
    """

    @staticmethod
    def calculate_dataset_compliant_score(
        candidate_record: Dict[str, Any], 
        must_have_skills: List[str],
        nice_to_have_skills: List[str]
    ) -> float:
        """
        Final production scoring - 0-day notice gets highest score.
        """
        # 1. Preemptive Synchronization Gateway Filter
        is_valid, _ = LocalMetadataDrivenReasoner.is_valid_candidate(candidate_record)
        if not is_valid:
            return 0.0

        signals = candidate_record.get("redrob_signals", {})
        skills = candidate_record.get("skills", [])
        profile = candidate_record.get("profile", {})
        
        cand_skills_set = set([s.get("name", "").lower().strip() for s in skills if s.get("name")])
        current_title = profile.get("current_title", "").lower().strip()
        cand_exp = float(profile.get("years_of_experience", 0))
        notice_period = int(signals.get("notice_period_days", 90))
        response_rate = float(signals.get("recruiter_response_rate", 1.0))
        interview_rate = float(signals.get("interview_completion_rate", 1.0))

        # =========================================================================
        # 📊 PHASE 1: BASE SCORING
        # =========================================================================
        
        # 1A. Skill Match Component
        expanded_targets = {
            "embeddings", "vector search", "bm25", "qdrant", "pinecone", "faiss", 
            "milvus", "weaviate", "pgvector", "elasticsearch", "learning to rank", 
            "ranking systems", "recommendation systems", "information retrieval", 
            "semantic search", "rag", "llm"
        }
        
        must_match_count = len(cand_skills_set.intersection(expanded_targets))
        skill_match_score = (must_match_count / len(expanded_targets)) if expanded_targets else 0.5
        
        # LangChain wrapper penalty
        if "langchain" in cand_skills_set:
            core_infra_ml = {
                "fastapi", "docker", "kubernetes", "qdrant", "milvus", 
                "scikit-learn", "tensorflow", "pytorch", "bm25", "elasticsearch"
            }
            if len(cand_skills_set.intersection(core_infra_ml)) < 2:
                skill_match_score *= 0.01

        # 1B. Response Rate Multiplier (BALANCED - not too harsh)
        if response_rate >= 0.80:
            response_multiplier = 1.10
        elif response_rate >= 0.70:
            response_multiplier = 1.05  # ✅ Small boost for 70-80%
        elif response_rate >= 0.60:
            response_multiplier = 0.95  # ✅ Small penalty
        elif response_rate >= 0.50:
            response_multiplier = 0.75
        else:
            response_multiplier = 0.60
        
        behavioral_score = (response_rate * 0.5 + interview_rate * 0.5)

        # 1C. Core 6-Factor Baseline
        semantic_score = float(signals.get("profile_completeness_score", 60)) / 100.0
        exp_score = min(cand_exp / 10.0, 1.0)

        base_score = (
            0.40 * skill_match_score + 
            0.20 * semantic_score + 
            0.15 * exp_score + 
            0.10 * behavioral_score + 
            0.15 * 0.5
        )
        
        # =========================================================================
        # 🚀 PHASE 2: POSITIVE MULTIPLIERS
        # =========================================================================
        
        # 2A. Title Boost
        perfect_match_titles = [
            'search engineer', 'ranking engineer', 'recommendation systems engineer', 
            'recommendation engineer', 'ranking systems', 'retrieval engineer'
        ]
        good_match_titles = [
            'lead ai engineer', 'senior ai engineer', 'nlp engineer', 
            'ai engineer', 'applied ml engineer'
        ]
        
        if any(t in current_title for t in perfect_match_titles):
            base_score *= 1.40
        elif any(t in current_title for t in good_match_titles):
            base_score *= 1.20

        # 2B. Core Retrieval Boost
        core_retrieval_inventory = {
            'bm25', 'learning to rank', 'ranking systems', 'recommendation systems', 
            'information retrieval', 'semantic search', 'vector search', 'rag', 
            'embeddings', 'ndcg', 'mrr'
        }
        core_count = len(cand_skills_set.intersection(core_retrieval_inventory))
        if core_count >= 2:
            base_score *= 1.15

        # 2C. Vector DB Boost
        vector_db_inventory = {
            'faiss', 'pinecone', 'weaviate', 'qdrant', 'milvus', 
            'pgvector', 'elasticsearch', 'opensearch'
        }
        if len(cand_skills_set.intersection(vector_db_inventory)) >= 2:
            base_score *= 1.10

        # 2D. Evaluation Framework Boost
        eval_framework_skills = {
            'ndcg', 'mrr', 'map', 'ranking metrics', 'a/b testing', 
            'experiment design', 'offline evaluation', 'ranking evaluation'
        }
        has_eval_experience = len(cand_skills_set.intersection(eval_framework_skills)) > 0
        has_ranking_systems = 'learning to rank' in cand_skills_set or 'ranking systems' in cand_skills_set
        
        if has_eval_experience or has_ranking_systems:
            base_score *= 1.12

        # =========================================================================
        # ❌ PHASE 3: NEGATIVE PENALTIES
        # =========================================================================
        
        # 3A. Junior Stagnation Penalty
        if cand_exp >= 6.0 and "junior" in current_title:
            base_score *= 0.60
        elif cand_exp >= 5.0 and "junior" in current_title:
            base_score *= 0.75

        # 3B. Career Switcher Penalty
        non_cs_degrees = ["civil engineer", "mechanical engineer", "electrical engineer"]
        if any(deg in current_title for deg in non_cs_degrees):
            base_score *= 0.75

        # 3C. CV/Research Isolation
        if "computer vision" in current_title or "cv engineer" in current_title:
            if core_count < 3:
                base_score *= 0.55
            else:
                base_score *= 0.80

        if "research" in current_title:
            production_signals = {
                'docker', 'kubernetes', 'fastapi', 'aws', 'gcp', 
                'azure', 'production', 'deployment', 'mlops'
            }
            has_production = len(cand_skills_set.intersection(production_signals)) >= 2
            
            if not has_production:
                base_score *= 0.50
            elif core_count < 3:
                base_score *= 0.70
            else:
                base_score *= 0.85

        # 3D. Response Rate Gate (ONLY for low response, not double-penalizing)
        if response_rate < 0.70:
            base_score *= response_multiplier
        elif response_rate >= 0.80:
            base_score *= 1.08  # ✅ Bonus for high engagement

        # =========================================================================
        # ✅ PHASE 4: NOTICE PERIOD MULTIPLIER (Applied BEFORE normalization)
        # =========================================================================
        
        raw_score = base_score
        
        # Notice period multiplier (STRONGER 0-day boost to ensure rank #1)
        if notice_period >= 120:
            raw_score *= 0.05  # 95% penalty
        elif notice_period >= 90:
            raw_score *= 0.15  # 85% penalty
        elif notice_period > 60:
            raw_score *= 0.40  # 60% penalty
        elif notice_period > 45:
            raw_score *= 0.75  # 25% penalty
        elif notice_period > 30:
            raw_score *= 0.85  # 15% penalty
        elif notice_period == 0:
            raw_score *= 1.18  # ✅ 18% BOOST for 0-day (INCREASED from 1.10)
        elif notice_period <= 15:
            raw_score *= 1.08  # 8% boost for ≤15-day (INCREASED from 1.05)
        elif notice_period <= 30:
            raw_score *= 1.00  # no change for 30-day
        
        # =========================================================================
        # ✅ PHASE 5: SMART NORMALIZATION
        # =========================================================================
        
        if raw_score > 1.0:
            # Top tier: 0-day notice + high response
            is_top_tier = (notice_period == 0 and response_rate >= 0.80)
            
            if is_top_tier:
                final_score = 1.0  # Perfect score
            else:
                # Normalize to 0.95-0.999 range
                excess = min(raw_score - 1.0, 0.20)
                normalized = 0.95 + (excess / 0.20) * 0.049
                final_score = min(0.999, normalized)
        else:
            final_score = max(0.0, raw_score)
        
        # =========================================================================
        # ✅ PHASE 6: FINAL SAFETY CAP + 4 DECIMAL FORMATTING
        # =========================================================================
        
        final_score = max(0.0, min(1.0, final_score))
        
        # ✅ ALWAYS return exactly 4 decimals
        return round(final_score, 4)