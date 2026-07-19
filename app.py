import streamlit as st

from charts import gauge_chart, radar_chart
from config import (
    APP_SUBTITLE,
    APP_TITLE,
    DISCLAIMER,
    LIKERT_OPTIONS,
    PAGE_ICON,
)
from data_loader import load_assessment_data
from recommendations import build_recommendations
from reporting import build_csv_report
from scoring import calculate_results


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 760;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 1.25rem;
    }

    .info-card {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

assessment_data = load_assessment_data()
dimensions = assessment_data["dimensions"]
questions = assessment_data["questions"]

st.markdown(
    f'<div class="hero-title">{PAGE_ICON} {APP_TITLE}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="hero-subtitle">{APP_SUBTITLE}</div>',
    unsafe_allow_html=True,
)

with st.expander("About this research prototype"):
    st.write(
        "This version uses a transparent weighted scoring engine. "
        "It is intended to validate the user experience, scoring structure, "
        "explainability, and recommendation logic before integration with a "
        "machine-learning model trained on the existing Qualtrics dataset."
    )

st.info(
    "Please answer all 18 statements. The current prototype uses a "
    "five-point agreement scale."
)

with st.form("erai_assessment"):
    st.subheader("Entrepreneurial Readiness Assessment")

    responses_text = {}

    tabs = st.tabs(
        [dimension["short_name"] for dimension in dimensions]
    )

    for tab, dimension in zip(tabs, dimensions):
        with tab:
            st.markdown(f"### {dimension['name']}")
            st.caption(dimension["description"])

            dimension_questions = [
                question
                for question in questions
                if question["dimension"] == dimension["id"]
            ]

            for question in dimension_questions:
                responses_text[question["id"]] = st.radio(
                    question["text"],
                    options=list(LIKERT_OPTIONS.keys()),
                    index=2,
                    horizontal=True,
                    key=question["id"],
                )

    submitted = st.form_submit_button(
        "Generate ERAI Assessment",
        type="primary",
        use_container_width=True,
    )

if submitted:
    responses_numeric = {
        question_id: LIKERT_OPTIONS[label]
        for question_id, label in responses_text.items()
    }

    results = calculate_results(
        responses=responses_numeric,
        dimensions=dimensions,
        questions=questions,
    )

    recommendations = build_recommendations(
        results["dimension_scores"]
    )

    st.divider()
    st.subheader("Assessment Results")

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        "ERAI Readiness Index",
        f"{results['overall_score']:.0f}/100",
    )

    metric_2.metric(
        "Readiness Level",
        results["readiness_level"],
    )

    metric_3.metric(
        "Strongest Dimension",
        results["strengths"][0]["name"],
    )

    st.success(results["interpretation"])

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            gauge_chart(results["overall_score"]),
            use_container_width=True,
        )

    with chart_right:
        st.plotly_chart(
            radar_chart(
                results["dimension_scores"],
                dimensions,
            ),
            use_container_width=True,
        )

    st.markdown("### Dimension Scores")

    for dimension in dimensions:
        score = results["dimension_scores"][dimension["id"]]

        st.write(
            f"**{dimension['name']}: {score:.0f}/100**"
        )

        st.progress(score / 100)

    st.markdown("### Explainable Assessment")

    st.write(
        "The overall index is a weighted combination of six readiness "
        "dimensions. Higher dimension scores contribute positively to the "
        "result, while lower scores are identified as development priorities."
    )

    strengths_col, gaps_col = st.columns(2)

    with strengths_col:
        st.markdown("#### Top Strengths")

        for item in results["strengths"]:
            st.success(
                f"{item['name']}: {item['score']:.0f}/100"
            )

    with gaps_col:
        st.markdown("#### Development Gaps")

        for item in results["gaps"]:
            st.warning(
                f"{item['name']}: {item['score']:.0f}/100"
            )

    st.markdown("### Personalized Recommendations")

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        st.markdown(
            f"**{number}. {recommendation['title']}**"
        )

        st.write(recommendation["action"])

    st.markdown("### Suggested Development Timeline")

    timeline_columns = st.columns(3)

    timeline_labels = [
        "Next 30 days",
        "30–90 days",
        "3–6 months",
    ]

    for column, label, recommendation in zip(
        timeline_columns,
        timeline_labels,
        recommendations,
    ):
        with column:
            st.markdown(f"**{label}**")
            st.write(recommendation["action"])

    csv_report = build_csv_report(
        responses_text=responses_text,
        responses_numeric=responses_numeric,
        results=results,
        dimensions=dimensions,
        questions=questions,
    )

    st.download_button(
        "Download Assessment Results (CSV)",
        data=csv_report,
        file_name="ERAI_Assessment_Results.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.caption(DISCLAIMER)
