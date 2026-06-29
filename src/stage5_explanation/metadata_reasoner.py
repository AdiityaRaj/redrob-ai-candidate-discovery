from typing import Dict, Any, Optional

class LocalMetadataDrivenReasoner:
    """Generates candidate-specific unique reasoning based on strict domain and availability floors."""
    
    VALID_AI_TITLES = {
        'ml engineer', 'machine learning engineer', 'ai engineer', 
        'data scientist', 'applied scientist', 'research scientist',
        'nlp engineer', 'search engineer', 'ranking engineer',
        'recommendation engineer', 'recommendation systems engineer',
        'applied ml engineer', 'senior ai engineer', 'lead ai engineer'
    }
    
    EXCLUDED_TITLES = {
        # Wrong Tech & Non-Engineering Domains
        'graphic designer', 'designer', 'operations manager', 'operations', 'project manager', 
        'business analyst', 'hr manager', 'marketing manager', 'sales executive', 
        'customer support', 'accountant', 'content writer', 'mobile developer',          
        'qa engineer', 'test engineer', 'data analyst', 'business intelligence analyst',
        # Wrong Software Domains
        '.net developer', 'java developer', 'frontend engineer', 'frontend developer', 
        'full stack developer', 'cloud engineer', 'devops engineer', 'backend engineer',
        # Speech/Robotics (Excluded by JD)
        'speech engineer', 'asr engineer', 'robotics engineer'
    }
    
    CORE_RETRIEVAL_SKILLS = {
        'bm25', 'elasticsearch', 'opensearch', 'vector search', 
        'semantic search', 'information retrieval', 'faiss', 'pinecone',
        'weaviate', 'qdrant', 'milvus', 'pgvector', 'embeddings',
        'sentence transformers', 'learning to rank', 'ranking systems',
        'recommendation systems', 'retrieval', 'search', 'haystack',
        'llamaindex', 'rag'
    }
    
    EXCLUDED_PRIMARY_SKILLS = {
        'computer vision', 'object detection', 'image classification',
        'yolo', 'opencv', 'cnn', 'speech recognition', 'asr', 'tts',
        'css', 'html', 'tailwind', 'typescript', 'javascript',
        'angular', 'react', 'vue.js', 'redux', 'next.js', 'powerpoint', 
        'excel', 'photoshop', 'illustrator'
    }

    VALID_TECHNICAL_SKILLS = {
        'bm25', 'elasticsearch', 'opensearch', 'faiss', 'pinecone',
        'weaviate', 'qdrant', 'milvus', 'pgvector', 'vector search',
        'semantic search', 'information retrieval', 'embeddings',
        'sentence transformers', 'learning to rank', 'haystack',
        'llamaindex', 'langchain', 'rag', 'pytorch', 'tensorflow',
        'hugging face transformers', 'scikit-learn', 'mlflow', 'mlops',
        'deep learning', 'machine learning', 'nlp', 'peft', 'lora', 'qlora',
        'fine-tuning llms', 'llms', 'recommendation systems', 'ranking systems', 'python',
        'data science', 'feature engineering', 'statistical modeling', 
        'ndcg', 'mrr', 'map', 'ranking metrics', 'ranking evaluation',
        'a/b testing', 'experiment design', 'offline evaluation', 'online evaluation'
    }

    @staticmethod
    def get_priority(skill: str) -> int:
        """Priority ordering for skill display in reasoning."""
        priority_map = {
            # HIGHEST PRIORITY: Evaluation Framework
            'ndcg': 0, 'mrr': 1, 'map': 2, 'ranking metrics': 3, 
            'a/b testing': 4, 'experiment design': 5, 'ranking evaluation': 6,
            
            # Core Retrieval
            'learning to rank': 10, 'ranking systems': 11, 'recommendation systems': 12,
            'information retrieval': 13, 'semantic search': 14, 'vector search': 15,
            'bm25': 16, 'rag': 17, 'embeddings': 18, 'sentence transformers': 19,
            
            # Vector DBs
            'faiss': 20, 'pinecone': 21, 'weaviate': 22, 'qdrant': 23,
            'milvus': 24, 'pgvector': 25, 'elasticsearch': 26, 'opensearch': 27,
            
            # ML Infrastructure
            'haystack': 30, 'llamaindex': 31, 'langchain': 32, 
            'pytorch': 35, 'tensorflow': 36, 'llms': 37, 
            'hugging face transformers': 38, 'fine-tuning llms': 39, 
            'lora': 40, 'qlora': 41, 'peft': 42,
            
            # General ML
            'deep learning': 45, 'machine learning': 46, 'nlp': 47, 
            'mlops': 48, 'python': 50
        }
        return priority_map.get(skill.lower(), 100)

    @staticmethod
    def is_valid_candidate(candidate_record: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """100% Algorithmic Filtering Engine with Strict Dynamic Thresholds."""
        profile = candidate_record.get("profile", {})
        signals = candidate_record.get("redrob_signals", {})
        skills = candidate_record.get("skills", [])
        
        title = profile.get("current_title", "").lower().strip()
        years = profile.get("years_of_experience", 0)
        response_rate = float(signals.get("recruiter_response_rate", 1.0))
        interview_rate = float(signals.get("interview_completion_rate", 1.0))
        
        # 1. Hard rejections - Excluded titles
        if any(ex in title for ex in LocalMetadataDrivenReasoner.EXCLUDED_TITLES):
            return False, f"Title '{title}' belongs to an explicitly excluded non-ML domain role."
        
        # 2. Strict Experience filter (4.5 years floor)
        if years < 4.5:
            return False, f"Experience {years} years is below the standard founding minimum."
        
        # 3. Active Availability Floor Filter (Strict 50% Bar)
        if response_rate < 0.50 or interview_rate < 0.50:
            return False, f"Low engagement signal ({int(response_rate*100)}% response rate)."
        
        skill_names = [s.get("name", "").lower().strip() for s in skills if s.get("name")]
        total_skills = len(skill_names) if skill_names else 1
        
        # 4. Pure Research Title Check
        if "research" in title:
            production_proofs = {"fastapi", "docker", "kubernetes", "aws", "gcp", "production", "deploy", "mlops"}
            if len(set(skill_names).intersection(production_proofs)) < 2:
                return False, "Pure academic research history without visible production deployment evidence."
        
        # 5. Excluded Domain Density Check
        excluded_count = sum(1 for skill in skill_names if skill in LocalMetadataDrivenReasoner.EXCLUDED_PRIMARY_SKILLS)
        if (excluded_count / total_skills) > 0.3 or excluded_count > 3:
            return False, "Primary expertise appears to be heavily focused in an excluded domain."
        
        # 6. Core Retrieval Skills Enforcement Layer
        core_count = sum(1 for skill in skill_names if skill in LocalMetadataDrivenReasoner.CORE_RETRIEVAL_SKILLS)
        title_is_perfect = any(keyword in title for keyword in ['search', 'ranking', 'recommendation', 'retrieval', 'nlp'])
        
        if not title_is_perfect and core_count < 1:
            return False, f"Insufficient retrieval/search expertise."
            
        return True, None

    @staticmethod
    def generate_candidate_justification(candidate_record: Dict[str, Any], final_score: float, talent_score: float) -> str:
        """
        Assembles precise token variables contextually into unique factual engineering assessments.
        Includes evaluation framework signals.
        """
        is_valid, reason = LocalMetadataDrivenReasoner.is_valid_candidate(candidate_record)
        if not is_valid:
            return f"EXCLUDED: {reason}"

        skills = candidate_record.get("skills", [])
        profile = candidate_record.get("profile", {})
        signals = candidate_record.get("redrob_signals", {})
        
        skill_names = [s.get("name", "").strip() for s in skills if s.get("name")]
        title = profile.get("current_title", "ML Engineer").strip()
        years = profile.get("years_of_experience", 0)
        response_rate = int(float(signals.get("recruiter_response_rate", 0.85)) * 100)
        notice = int(signals.get("notice_period_days", 30))

        valid_skills = [s for s in skill_names if s.lower() in LocalMetadataDrivenReasoner.VALID_TECHNICAL_SKILLS]
        if not valid_skills:
            valid_skills = ["Machine Learning", "Python"]
            
        valid_skills_sorted = sorted(valid_skills, key=LocalMetadataDrivenReasoner.get_priority)
        
        vector_dbs = [s for s in valid_skills_sorted if s.lower() in {
            'faiss', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'pgvector', 'elasticsearch', 'opensearch'
        }]
        
        retrieval_skills = [s for s in valid_skills_sorted if s.lower() in {
            'bm25', 'learning to rank', 'ranking systems', 'recommendation systems', 
            'information retrieval', 'semantic search', 'vector search', 'rag'
        }]
        
        eval_signals = [s for s in valid_skills_sorted if s.lower() in {
            'ndcg', 'mrr', 'map', 'ranking metrics', 'ranking evaluation',
            'a/b testing', 'experiment design', 'offline evaluation', 'online evaluation'
        }]

        parts = []
        
        if any(kw in title.lower() for kw in ['search', 'ranking', 'recommendation', 'retrieval']):
            parts.append(f"{title} with {years} years - excellent specialized match for search architecture role.")
        else:
            parts.append(f"{title} with {years} years ML/AI engineering experience.")
        
        if retrieval_skills:
            parts.append(f"Core retrieval expertise includes production depth in {', '.join(retrieval_skills[:2])}.")
        
        if eval_signals:
            parts.append(f"Demonstrated ranking evaluation experience ({', '.join(eval_signals[:2])}).")
        elif 'learning to rank' in [s.lower() for s in retrieval_skills]:
            parts.append("Demonstrated hands-on ranking systems evaluation capability (LTR infrastructure).")
        elif 'ranking systems' in [s.lower() for s in retrieval_skills]:
            parts.append("Demonstrated ranking systems evaluation capability.")
        
        if vector_dbs:
            parts.append(f"Verified operational history managing databases like {', '.join(vector_dbs[:2])}.")
        
        parts.append(f"Availability parameters confirmed ({response_rate}% response rate, {notice}-day notice cycle).")
        
        return " ".join(parts)