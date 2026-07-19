# reporting.py
"""
EntreReady AI (ERAI) — Report generation.
Builds a downloadable CSV report from the assessment results.
Standard library + pandas only (pandas is already in requirements.txt).
"""

import io
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


def build_csv_report(
    responses_text: Dict[str, str],
    responses_numeric: Dict[str, int],
    results: Dict[str, Any],
    dimensions: List[Dict[str, Any]],
) -> bytes:
    """
    Build a UTF-8 CSV report of the assessment results.

    Parameters
    ----------
    responses_text : dict
        {question_id: selected Likert text} e.g. {"Q7": "Agree"}
    responses_numeric : dict
        {question_id: numeric score 1-5} e.g. {"Q7": 4}
    results : dict
        Output of scoring.calculate_results(). Expected keys:
        - overall_score (float)
        - readiness_level (str)
        - dimension_scores (dict: dimension_id -> score)
        - strengths (list of {"name": str, "score": float})
        - gaps (list of {"name": str, "score": float})
    dimensions : list of dict
        The DIMENSIONS metadata, each {"id": str, "name": str, "weight": float, ...}

    Returns
    -------
    bytes
        UTF-8 encoded CSV, ready for st.download_button.
    """
    buffer = io.StringIO()

    # --- Section 1: Report header / metadata ---
    buffer.write("EntreReady AI (ERAI) — Assessment Report\n")
    buffer.write(f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    buffer.write("\n")

    # --- Section 2: Overall result ---
    buffer.write("Overall Result\n")
    overall = pd.DataFrame(
        {
            "Metric": ["Overall Readiness Index", "Readiness Level"],
            "Value": [
                f"{results.get('overall_score', 0):.1f}",
                results.get("readiness_level", "N/A"),
            ],
        }
    )
    buffer.write(overall.to_csv(index=False))
    buffer.write("\n")

    # --- Section 3: Dimension scores ---
    buffer.write("Dimension Scores\n")
    # Map dimension id -> display name using the dimensions metadata
    name_by_id = {d.get("id"): d.get("name", d.get("id")) for d in (dimensions or [])}
    dim_scores = results.get("dimension_scores") or {}
    dim_df = pd.DataFrame(
        {
            "Dimension": [name_by_id.get(k, k) for k in dim_scores.keys()],
            "Score": [f"{v:.1f}" for v in dim_scores.values()],
        }
    )
    buffer.write(dim_df.to_csv(index=False))
    buffer.write("\n")

    # --- Section 4: Strengths ---
    buffer.write("Strengths\n")
    strengths = results.get("strengths") or []
    strengths_df = pd.DataFrame(
        {
            "Dimension": [s.get("name", "") for s in strengths],
            "Score": [f"{s.get('score', 0):.1f}" for s in strengths],
        }
    )
    buffer.write(strengths_df.to_csv(index=False))
    buffer.write("\n")

    # --- Section 5: Development gaps ---
    buffer.write("Development Gaps\n")
    gaps = results.get("gaps") or []
    gaps_df = pd.DataFrame(
        {
            "Dimension": [g.get("name", "") for g in gaps],
            "Score": [f"{g.get('score', 0):.1f}" for g in gaps],
        }
    )
    buffer.write(gaps_df.to_csv(index=False))
    buffer.write("\n")

    # --- Section 6: Detailed responses ---
    buffer.write("Detailed Responses\n")
    qids = list(responses_text.keys()) if responses_text else []
    responses_df = pd.DataFrame(
        {
            "Question ID": qids,
            "Answer (Text)": [responses_text.get(q, "") for q in qids],
            "Answer (Score)": [responses_numeric.get(q, "") for q in qids],
        }
    )
    buffer.write(responses_df.to_csv(index=False))

    return buffer.getvalue().encode("utf-8")
