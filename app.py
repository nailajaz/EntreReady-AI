from pathlib import Path
import textwrap, json, zipfile, os

base = Path("/mnt/data/EntreReady-AI")
base.mkdir(exist_ok=True)

app_py = r'''
import io
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from scoring import DIMENSIONS, QUESTIONS, calculate_results
from recommendations import build_recommendations

st.set_page_config(
    page_title="EntreReady AI (ERAI)",
    page_icon="🚀",
    layout="wide",
)

CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
.main-title {font-size: 2.3rem; font-weight: 750; margin-bottom: .25rem;}
.subtitle {font-size: 1.05rem; color: #5f6368; margin-bottom: 1rem;}
.small-note {font-size: .88rem; color: #666;}
.result-box {
    border: 1px solid rgba(128,128,128,.28);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: .75rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 EntreReady AI (ERAI)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">An Explainable AI Decision Support Framework for Assessing '
    'Entrepreneurial Readiness, Identifying Development Gaps, and Providing Personalized Recommendations</div>',
    unsafe_allow_html=True,
)

with st.expander("About this prototype", expanded=False):
    st.write(
        "This Version 1 prototype uses a transparent, weighted assessment engine. "
        "It does not yet use a machine-learning model trained on the Qualtrics dataset. "
        "The scoring logic is intentionally explainable so that the assessment flow, outputs, "
        "and recommendations can be reviewed before model integration."
    )

LIKERT = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

with st.form("erai_assessment"):
    st.subheader("Quick Entrepreneurial Readiness Assessment")
    st.caption("Select the response that best reflects your current position.")

    responses = {}
    tabs = st.tabs([d["short_name"] for d in DIMENSIONS])

    for tab, dimension in zip(tabs, DIMENSIONS):
        with tab:
            st.markdown(f"### {dimension['name']}")
            st.caption(dimension["description"])
            for q in [x for x in QUESTIONS if x["dimension"] == dimension["id"]]:
                responses[q["id"]] = st.radio(
                    q["text"],
                    options=list(LIKERT.keys()),
                    index=2,
                    horizontal=True,
                    key=q["id"],
                )

    submitted = st.form_submit_button(
        "Generate ERAI Assessment",
        type="primary",
        use_container_width=True,
    )

if submitted:
    numeric_responses = {qid: LIKERT[label] for qid, label in responses.items()}
    results = calculate_results(numeric_responses)
    recommendations = build_recommendations(results["dimension_scores"])

    st.divider()
    st.subheader("Your ERAI Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("ERAI Readiness Index", f"{results['overall_score']:.0f}/100")
    c2.metric("Readiness Level", results["readiness_level"])
    c3.metric("Strongest Dimension", results["strengths"][0]["name"])

    st.progress(results["overall_score"] / 100)
    st.caption(results["interpretation"])

    left, right = st.columns([1.15, 1])

    with left:
        fig = go.Figure()
        labels = [d["name"] for d in DIMENSIONS]
        values = [results["dimension_scores"][d["id"]] for d in DIMENSIONS]
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill="toself",
                name="Readiness score",
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=30, r=30, t=35, b=30),
            title="Entrepreneurial Readiness Profile",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Dimension Scores")
        for d in DIMENSIONS:
            score = results["dimension_scores"][d["id"]]
            st.write(f"**{d['name']} — {score:.0f}/100**")
            st.progress(score / 100)

    st.markdown("### Explainable Assessment")
    st.write(
        "The result is produced from six readiness dimensions. The strongest dimensions "
        "increase the overall readiness assessment, while lower-scoring dimensions are flagged "
        "as development priorities."
    )

    e1, e2 = st.columns(2)
    with e1:
        st.markdown("#### Top Strengths")
        for item in results["strengths"]:
            st.success(f"{item['name']}: {item['score']:.0f}/100")

    with e2:
        st.markdown("#### Development Gaps")
        for item in results["gaps"]:
            st.warning(f"{item['name']}: {item['score']:.0f}/100")

    st.markdown("### Personalized Recommendations")
    for idx, rec in enumerate(recommendations, start=1):
        st.markdown(f"**{idx}. {rec['title']}**")
        st.write(rec["action"])

    st.markdown("### Suggested Development Timeline")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("**Next 30 days**")
        st.write(recommendations[0]["action"])
    with t2:
        st.markdown("**30–90 days**")
        st.write(recommendations[1]["action"])
    with t3:
        st.markdown("**3–6 months**")
        st.write(recommendations[2]["action"])

    export_rows = []
    for q in QUESTIONS:
        export_rows.append({
            "question_id": q["id"],
            "dimension": q["dimension"],
            "question": q["text"],
            "response": responses[q["id"]],
            "score": numeric_responses[q["id"]],
        })

    export_df = pd.DataFrame(export_rows)
    summary_df = pd.DataFrame([
        {"metric": "ERAI Readiness Index", "value": round(results["overall_score"], 1)},
        {"metric": "Readiness Level", "value": results["readiness_level"]},
        *[
            {"metric": d["name"], "value": round(results["dimension_scores"][d["id"]], 1)}
            for d in DIMENSIONS
        ],
    ])

    output = io.StringIO()
    output.write("EntreReady AI (ERAI) Assessment\n")
    output.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
    output.write("SUMMARY\n")
    summary_df.to_csv(output, index=False)
    output.write("\nRESPONSES\n")
    export_df.to_csv(output, index=False)

    st.download_button(
        "Download Assessment Results (CSV)",
        data=output.getvalue(),
        file_name="ERAI_Assessment_Results.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.caption(
    "Research prototype only. ERAI does not determine whether a person will become an entrepreneur. "
    "It provides a current readiness assessment based on self-reported responses and identifies areas for development."
)
'''

scoring_py = r'''
DIMENSIONS = [
    {
        "id": "motivation",
        "name": "Entrepreneurial Motivation",
        "short_name": "Motivation",
        "description": "Commitment, career intention, and willingness to pursue venture creation.",
        "weight": 0.18,
    },
    {
        "id": "self_efficacy",
        "name": "Entrepreneurial Self-Efficacy",
        "short_name": "Self-Efficacy",
        "description": "Confidence in planning, decision-making, leadership, and problem solving.",
        "weight": 0.20,
    },
    {
        "id": "innovation",
        "name": "Innovation & Opportunity Recognition",
        "short_name": "Innovation",
        "description": "Ability to recognize needs, generate ideas, and test new solutions.",
        "weight": 0.18,
    },
    {
        "id": "resilience",
        "name": "Risk Management & Resilience",
        "short_name": "Resilience",
        "description": "Readiness to manage uncertainty, calculated risk, setbacks, and change.",
        "weight": 0.16,
    },
    {
        "id": "business_ai",
        "name": "Business & AI Readiness",
        "short_name": "Business & AI",
        "description": "Business knowledge, data use, digital capability, and responsible use of AI.",
        "weight": 0.18,
    },
    {
        "id": "support",
        "name": "Resources & Support",
        "short_name": "Support",
        "description": "Access to networks, mentors, information, education, and other enabling resources.",
        "weight": 0.10,
    },
]

QUESTIONS = [
    {"id": "M1", "dimension": "motivation", "text": "Starting or developing a venture is an important career goal for me."},
    {"id": "M2", "dimension": "motivation", "text": "I am willing to invest sustained effort in pursuing a business opportunity."},
    {"id": "M3", "dimension": "motivation", "text": "I actively look for opportunities that could become viable ventures."},

    {"id": "S1", "dimension": "self_efficacy", "text": "I am confident that I can evaluate whether a business idea is feasible."},
    {"id": "S2", "dimension": "self_efficacy", "text": "I can make decisions when business information is incomplete."},
    {"id": "S3", "dimension": "self_efficacy", "text": "I am confident that I can organize people and resources around a business goal."},

    {"id": "I1", "dimension": "innovation", "text": "I can identify unmet customer or community needs."},
    {"id": "I2", "dimension": "innovation", "text": "I frequently generate practical ideas for solving problems."},
    {"id": "I3", "dimension": "innovation", "text": "I am willing to test and improve an idea using feedback."},

   
