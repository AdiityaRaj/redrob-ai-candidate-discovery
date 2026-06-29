import json
import csv
import argparse
import os
from src.config import CANDIDATES_JSONL, SAMPLE_JD_DOCX, SUBMISSION_CSV
from src.utils.logger import logger
from src.stage1_parser.local_nlp_parser import LocalNLPJDParser
from src.stage4_reranking.honeypot_detector import HoneypotTrapDetector
from src.stage4_reranking.hidden_talent import HiddenTalentEngine
from src.stage4_reranking.business_rules import ProductionBusinessRulesEngine
from src.stage5_explanation.metadata_reasoner import LocalMetadataDrivenReasoner

def execute_pipeline(jd_path: str, candidates_path: str, output_path: str):
    """
    Final Dataset-Compliant Pipeline Controller for Redrob AI Hackathon.
    Implements strict 6-factor fusion formulas and drops Simple Keyword Counts.
    """
    logger.info("=== [Rank 1] Redrob AI Dataset-Compliant Pipeline Triggered ===")
    
    # 1. Initialize Compliant System Engines
    parser = LocalNLPJDParser()
    honeypot_filter = HoneypotTrapDetector()
    
    if not os.path.exists(jd_path):
        logger.error(f"Target Job Description document missing at: {jd_path}")
        return

    # 2. Stage 1: Parse Input Job Description
    parsed_jd = parser.parse_job_description(jd_path)
    must_have_skills = parsed_jd.get("must_have_skills", [])
    nice_to_have_skills = parsed_jd.get("nice_to_have_skills", [])

    logger.info(f"Streaming candidate collection from: {candidates_path}")
    final_scored_pool = []
    
    if not os.path.exists(candidates_path):
        logger.error(f"Candidates database asset missing at: {candidates_path}")
        return

    processed_count = 0
    honeypots_dropped = 0

    # 3. Process 100,000 Candidates in a Fast Streaming CPU Loop
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            
            cand_data = json.loads(line)
            processed_count += 1
            
            # Keep track of heavy console execution progress signs
            if processed_count % 20000 == 0:
                logger.info(f"Validated and parsed {processed_count} candidate nodes...")

            # 4. Stage 4.3.1: Honeypot Consistency Check (Instant Disqualification Layer)
            is_fraud, violation_msg = honeypot_filter.inspect_candidate(cand_data)
            if is_fraud:
                honeypots_dropped += 1
                continue # Safely filters fake profile payloads

            c_id = cand_data.get("candidate_id")
            
            # 5. Stage 4.3.2: Execute Mathematical Underdog Engine
            talent_score, classification = HiddenTalentEngine.evaluate_underdog_index(cand_data)
            
            # 6. Stage 4.4 & 4.5: Calculate the Official 6-Factor Hybrid Ranking Formula
            # Fully compliant with Page 5 weights using structured skills over text counts
            final_score = ProductionBusinessRulesEngine.calculate_dataset_compliant_score(
                candidate_record=cand_data,
                must_have_skills=must_have_skills,
                nice_to_have_skills=nice_to_have_skills
            )
            
            # 7. Stage 5: Local Fact-Grounded Template Reasoning Engine
            reasoning = LocalMetadataDrivenReasoner.generate_candidate_justification(
                candidate_record=cand_data,
                final_score=final_score,
                talent_score=talent_score
            )
            
            final_scored_pool.append({
                "candidate_id": c_id,
                "score": final_score,
                "talent_score": talent_score,
                "reasoning": reasoning
            })

    logger.info(f"Ingestion Complete. Total Processed: {processed_count}. Dropped {honeypots_dropped} honeypots.")

    # 8. Stage 6: Strict Sorting, Truncation & Tie-Breaking Rules Execution
    # Sort hierarchy: Bounded Score Descending, Tie-breaker Candidate ID Ascending
    final_scored_pool.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Strict boundary lock: slice to extract exactly top 100 entries
    top_100_final = final_scored_pool[:100]

    # 9. Export to Compliant submission.csv Output Matrix
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for idx, entry in enumerate(top_100_final, start=1):
            writer.writerow([
                entry["candidate_id"],
                idx,
                round(entry["score"], 4),
                entry["reasoning"]
            ])

    logger.info(f"🎉 Success! Submission matrix generated with exactly {len(top_100_final)} rows.")
    logger.info(f"Target Output Path Safe: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", default=str(SAMPLE_JD_DOCX), help="Path to input job description docx")
    parser.add_argument("--candidates", default=str(CANDIDATES_JSONL), help="Path to raw candidates jsonl dataset")
    parser.add_argument("--out", default=str(SUBMISSION_CSV), help="Target output csv submission path")
    args = parser.parse_args()
    
    execute_pipeline(args.jd, args.candidates, args.out)
