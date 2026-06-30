import streamlit as st
import streamlit as str_st
import pandas as pd
import json
import sys
import os
from typing import Optional, List, Dict, Tuple
from io import BytesIO

# Absolute path safeguard fallback lane
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.stage5_explanation.metadata_reasoner import LocalMetadataDrivenReasoner
from src.stage4_reranking.business_rules import ProductionBusinessRulesEngine  # keep your path

# -----------------------------
# OPTIONAL: DOCX JD parsing
# -----------------------------
try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

# Paths
JD_DOCX_PATH = "data/raw/job_description.docx"
JD_MD_FALLBACK = "job_description.md"

# Curated demo sample (commit this file)
DEMO_SAMPLE_PATHS = [
    "data/sandbox/curated_demo_candidates.jsonl",
    "data/sandbox/curated_demo_candidates.json",
    "sample_candidates.json",
]

DEMO_NOTE = "Demo sample contains 100 candidates pre-selected from our final shortlist to showcase ranking behavior."

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Redrob AI Candidate Discovery Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Styling (your premium CSS preserved)
# -----------------------------
st.markdown("""<style>
.reportview-container .main .block-container { max-width: 100%; padding-left: 2rem; padding-right: 2rem; }
h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #f8fafc; }
.scroll-container { width: 100%; max-height: 550px; overflow-x: auto !important; overflow-y: auto !important;
border: 1px solid #334155; border-radius: 8px; background-color: #0f172a; }
.dataframe-table { width: 100%; border-collapse: collapse; color: #e2e8f0; font-family: 'Inter', sans-serif; font-size: 14px; }
.dataframe-table th { background-color: #1e293b; color: #3b82f6; padding: 12px; text-align: left; position: sticky;
top: 0; border-bottom: 2px solid #334155; z-index: 10; font-weight: 600; white-space: nowrap; }
.dataframe-table td { padding: 12px; border-bottom: 1px solid #1e293b; vertical-align: top; }
.reasoning-cell { min-width: 450px; white-space: normal !important; word-wrap: break-word; color: #cbd5e1; line-height: 1.5; }
</style>""", unsafe_allow_html=True)

# -----------------------------
# Session state init
# -----------------------------
def init_state():
    st.session_state.setdefault("df_ranked", None)
    st.session_state.setdefault("df_rejected", None)
    st.session_state.setdefault("execution_logs", [])
    st.session_state.setdefault("run_stats", {})
    st.session_state.setdefault("input_mode", "Upload sample")
    st.session_state.setdefault("last_source", "")

init_state()

# -----------------------------
# Helpers
# -----------------------------
def load_jd_text() -> str:
    if os.path.exists(JD_DOCX_PATH):
        if not DOCX_AVAILABLE:
            return f"[ERROR] python-docx not installed; cannot read {JD_DOCX_PATH}"
        try:
            doc = Document(JD_DOCX_PATH)
            paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            return "\n".join(paras).strip()
        except Exception as e:
            return f"[ERROR] Failed reading DOCX: {e}"

    if os.path.exists(JD_MD_FALLBACK):
        try:
            with open(JD_MD_FALLBACK, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            return f"[ERROR] Failed reading MD fallback: {e}"

    return ""


def parse_candidates_text(raw: str) -> List[Dict]:
    raw = (raw or "").strip()
    if not raw:
        return []

    # Try JSON list
    try:
        obj = json.loads(raw)
        if isinstance(obj, list):
            return obj
    except json.JSONDecodeError:
        pass

    # JSONL fallback
    records = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def parse_candidates_file(uploaded_file) -> List[Dict]:
    raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    return parse_candidates_text(raw)


def load_candidates_from_path(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    return parse_candidates_text(raw)


def find_demo_sample_path() -> Optional[str]:
    for p in DEMO_SAMPLE_PATHS:
        if os.path.exists(p):
            return p
    return None


def rank_candidates_with_rejections(records: List[Dict], top_k: int = 100) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    ranked = []
    rejected = []

    for rec in records:
        cid = (rec.get("candidate_id") or "").strip()
        profile = rec.get("profile", {}) or {}
        signals = rec.get("redrob_signals", {}) or {}

        if not cid:
            rejected.append({
                "candidate_id": "",
                "title": profile.get("current_title", ""),
                "years": profile.get("years_of_experience", ""),
                "response_rate": signals.get("recruiter_response_rate", ""),
                "interview_rate": signals.get("interview_completion_rate", ""),
                "notice_days": signals.get("notice_period_days", ""),
                "reject_reason": "Missing candidate_id"
            })
            continue

        ok, reason = LocalMetadataDrivenReasoner.is_valid_candidate(rec)
        if not ok:
            rejected.append({
                "candidate_id": cid,
                "title": profile.get("current_title", ""),
                "years": profile.get("years_of_experience", ""),
                "response_rate": signals.get("recruiter_response_rate", ""),
                "interview_rate": signals.get("interview_completion_rate", ""),
                "notice_days": signals.get("notice_period_days", ""),
                "reject_reason": reason or "Rejected by eligibility gate"
            })
            continue

        score = ProductionBusinessRulesEngine.calculate_dataset_compliant_score(rec, [], [])
        if score <= 0:
            rejected.append({
                "candidate_id": cid,
                "title": profile.get("current_title", ""),
                "years": profile.get("years_of_experience", ""),
                "response_rate": signals.get("recruiter_response_rate", ""),
                "interview_rate": signals.get("interview_completion_rate", ""),
                "notice_days": signals.get("notice_period_days", ""),
                "reject_reason": "Score <= 0 after business rules"
            })
            continue

        reasoning = LocalMetadataDrivenReasoner.generate_candidate_justification(rec, score, score)

        ranked.append({
            "candidate_id": cid,
            "rank": 0,
            "score": float(score),
            "reasoning": reasoning
        })

    ranked.sort(key=lambda r: (-r["score"], r["candidate_id"]))
    ranked = ranked[:top_k]

    for i, r in enumerate(ranked, 1):
        r["rank"] = i
        r["score"] = f"{r['score']:.4f}"

    df_ranked = pd.DataFrame(ranked, columns=["candidate_id", "rank", "score", "reasoning"])
    df_rejected = pd.DataFrame(
        rejected,
        columns=["candidate_id", "title", "years", "response_rate", "interview_rate", "notice_days", "reject_reason"]
    )

    stats = {"loaded": len(records), "ranked": len(df_ranked), "rejected": len(df_rejected)}
    return df_ranked, df_rejected, stats


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_ranked_html_table(df: pd.DataFrame):
    html_buffer = ["<div class='scroll-container'><table class='dataframe-table'>"]
    html_buffer.append("<thead><tr><th>Candidate ID</th><th>Rank</th><th>Score</th><th>Reasoning</th></tr></thead>")
    html_buffer.append("<tbody>")

    for _, row in df.iterrows():
        html_buffer.append("<tr>")
        html_buffer.append(f"<td><code style='color:#f43f5e; font-weight:bold;'>{row['candidate_id']}</code></td>")
        html_buffer.append(f"<td><span style='color:#10b981; font-weight:600;'>#{int(row['rank'])}</span></td>")
        html_buffer.append(f"<td><code style='color:#3b82f6;'>{row['score']}</code></td>")
        html_buffer.append(f"<td class='reasoning-cell'>{row['reasoning']}</td>")
        html_buffer.append("</tr>")

    html_buffer.append("</tbody></table></div>")
    st.markdown("".join(html_buffer), unsafe_allow_html=True)


def clear_outputs():
    st.session_state["df_ranked"] = None
    st.session_state["df_rejected"] = None
    st.session_state["execution_logs"] = []
    st.session_state["run_stats"] = {}
    st.session_state["last_source"] = ""


# -----------------------------
# Header
# -----------------------------
st.title("Redrob AI Candidate Discovery & Ranking Hub")
st.subheader("CPU-Only, Network-Free Match Engine (Sandbox Demo)")
st.markdown("---")

# -----------------------------
# JD Display
# -----------------------------
jd_text = load_jd_text()
with st.expander("Job Description (Loaded from repo)", expanded=False):
    if not jd_text.strip():
        st.warning(f"JD not found. Expected: {JD_DOCX_PATH} (or {JD_MD_FALLBACK}).")
    else:
        st.text_area("JD (read-only)", jd_text, height=280)

# -----------------------------
# Layout
# -----------------------------
left_panel, right_panel = st.columns([1, 3])

# -----------------------------
# Left panel: Inputs
# -----------------------------
with left_panel:
    st.markdown("### Sandbox Input")

    st.session_state["input_mode"] = st.radio(
        "Choose input mode",
        options=["Upload sample", "Use built-in demo sample"],
        index=0 if st.session_state["input_mode"] == "Upload sample" else 1
    )

    uploaded = None
    demo_path = None

    if st.session_state["input_mode"] == "Upload sample":
        uploaded = st.file_uploader(
            "Upload sample candidates (≤100) as .json (list) or .jsonl",
            type=["json", "jsonl"]
        )
        st.caption("Tip: Use ≤100 candidates for fast sandbox execution.")
    else:
        demo_path = find_demo_sample_path()
        if demo_path:
            st.success(f"Demo sample found: {demo_path}")
            st.caption(DEMO_NOTE)  # ✅ your requested line
        else:
            st.error("No demo sample found in repo. Add one at data/sandbox/curated_demo_candidates.jsonl")

    col_a, col_b = st.columns(2)
    with col_a:
        run = st.button(
            "Run Ranking",
            use_container_width=True,
            disabled=(uploaded is None and demo_path is None)
        )
    with col_b:
        reset = st.button("Clear", use_container_width=True)

    if reset:
        clear_outputs()

    if run:
        if uploaded is not None:
            records = parse_candidates_file(uploaded)
            source = "uploaded_sample"
        else:
            records = load_candidates_from_path(demo_path)
            source = f"demo_sample:{demo_path}"

        # enforce sandbox constraint (≤100)
        if len(records) > 100:
            records = records[:100]
            st.warning("Input had >100 candidates; truncated to first 100 for sandbox constraints.")

        st.session_state["execution_logs"] = [f"Loaded: {len(records)} candidates (source={source})."]

        with st.spinner("Running eligibility gate + scoring + deterministic sorting..."):
            df_ranked, df_rejected, stats = rank_candidates_with_rejections(records, top_k=100)

        st.session_state["df_ranked"] = df_ranked
        st.session_state["df_rejected"] = df_rejected
        st.session_state["run_stats"] = stats
        st.session_state["last_source"] = source

        st.session_state["execution_logs"].append(
            f"Done. Ranked: {stats['ranked']} | Rejected: {stats['rejected']}"
        )

    for log in st.session_state["execution_logs"]:
        st.write(log)

    if st.session_state.get("run_stats"):
        stt = st.session_state["run_stats"]
        st.caption(f"Stats → Loaded: {stt.get('loaded',0)}, Ranked: {stt.get('ranked',0)}, Rejected: {stt.get('rejected',0)}")

# -----------------------------
# Right panel: Output
# -----------------------------
with right_panel:
    st.markdown("### Ranked Output (Top-K from selected input)")
    st.caption("Reasoning is generated deterministically from candidate fields; no external API calls.")

    df_ranked = st.session_state.get("df_ranked")
    df_rejected = st.session_state.get("df_rejected")
    stats = st.session_state.get("run_stats") or {}

    if df_ranked is None or df_ranked.empty:
        st.info("Choose an input mode and click 'Run Ranking' to generate output.")
    else:
        ranked_n = stats.get("ranked", len(df_ranked))
        if ranked_n < 100:
            st.warning(
                f"Only {ranked_n} candidates passed the eligibility gate in this sample. "
                "This is expected for random samples with many out-of-scope titles."
            )

        # extra context if demo sample used
        if str(st.session_state.get("last_source", "")).startswith("demo_sample:"):
            st.info(DEMO_NOTE)

        render_ranked_html_table(df_ranked)

        st.markdown("---")
        st.download_button(
            label="Download ranked CSV (sandbox)",
            data=df_to_csv_bytes(df_ranked),
            file_name="submission_sandbox.csv",
            mime="text/csv",
            use_container_width=True
        )

    with st.expander("Rejected Candidates (show reasons)", expanded=False):
        if df_rejected is None or df_rejected.empty:
            st.info("No rejected candidates to show.")
        else:
            if "reject_reason" in df_rejected.columns:
                st.markdown("#### Top rejection reasons")
                st.write(df_rejected["reject_reason"].value_counts().head(10))

            st.markdown("#### Rejected rows")
            st.dataframe(df_rejected, use_container_width=True, height=260)

            st.download_button(
                label="Download rejected_report.csv",
                data=df_to_csv_bytes(df_rejected),
                file_name="rejected_report.csv",
                mime="text/csv",
                use_container_width=True
            )