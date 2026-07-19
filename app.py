import streamlit as st

from charts import gauge_chart, radar_chart
from config import (
    APP_SUBTITLE,
    APP_TITLE,
    DISCLAIMER,
    LIKERT_OPTIONS,
    PAGE_ICON,
    QUESTIONS,
    DEMOGRAPHICS,
)
from recommendations import build_recommendations
from reporting import build_csv_report
from scoring import calculate_results

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"
if "mode" not in st.session_state:
    st.session_state.mode = None


def go_to(page):
    st.session_state.page = page


def render_home():
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.write(
        "EntreReady AI evaluates your entrepreneurial readiness across six "
        "dimensions and returns a transparent readiness index, your strongest "
        "and weakest areas, and personalized next steps."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎓 Student / University")
        if st.button("Start Student Assessment", use_container_width=True):
            st.session_state.mode = "Student"
            go_to("intake")
    with c2:
        st.subheader("🌍 Public / Professional")
        if st.button("Start Public Assessment", use_container_width=True):
            st.session_state.mode = "Public"
            go_to("intake")
    st.info(DISCLAIMER)


def render_intake():
    mode = st.session_state.mode
    st.header(f"{mode} Intake")
    st.caption("These details personalize your recommendations. They are not scored.")
    demo_answers = {}
    for key, meta in DEMOGRAPHICS.items():
        demo_answers[key] = st.selectbox(meta["label"], meta["options"], key=f"demo_{key}")
    st.session_state.demographics = demo_answers
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", use_container_width=True):
            go_to("home")
    with c2:
        if st.button("Continue to Assessment →", use_container_width=True):
            go_to("assessment")


def render_assessment():
    st.header("Readiness Assessment")
    st.caption("Rate how strongly you agree with each statement.")
    responses = {}
    for dimension, items in QUESTIONS.items():
        st.subheader(dimension)
        for qid, text in items.items():
            choice = st.radio(
                text,
                options=list(LIKERT_OPTIONS.keys()),
                horizontal=True,
                key=f"q_{qid}",
                index=2,
            )
            responses[qid] = LIKERT_OPTIONS[choice]
        st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", use_container_width=True):
            go_to("intake")
    with c2:
        if st.button("See My Results →", type="primary", use_container_width=True):
            st.session_state.responses = responses
            go_to("results")


def render_results():
    mode = st.session_state.mode
    responses = st.session_state.get("responses", {})
    if not responses:
        st.warning("No responses found. Please complete the assessment.")
        if st.button("Start Over"):
            go_to("home")
        return

    results = calculate_results(responses)
    readiness_index = results["readiness_index"]
    classification = results["classification"]
    dimension_scores = results["dimension_scores"]

    st.header("Your Entrepreneurial Readiness")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(gauge_chart(readiness_index, classification), use_container_width=True)
    with col2:
        st.plotly_chart(radar_chart(dimension_scores), use_container_width=True)

    st.subheader(f"Overall Classification: {classification}")

    recommendations = build_recommendations(
        dimension_scores=dimension_scores,
        mode=mode,
    )

    st.subheader("Development Gaps to Address")
    for gap in recommendations["gaps"]:
        st.markdown(f"- **{gap['dimension']}** — {gap['message']}")

    st.subheader("Recommended Next Steps")
    for rec in recommendations["actions"]:
        st.markdown(f"- {rec}")

    csv_bytes = build_csv_report(
        mode=mode,
        demographics=st.session_state.get("demographics", {}),
        dimension_scores=dimension_scores,
        readiness_index=readiness_index,
        classification=classification,
    )
    st.download_button(
        label="⬇️ Download My Results (CSV)",
        data=csv_bytes,
        file_name="entreready_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("Start Over"):
        for key in ("responses", "demographics", "mode"):
            st.session_state.pop(key, None)
        go_to("home")


PAGES = {
    "home": render_home,
    "intake": render_intake,
    "assessment": render_assessment,
    "results": render_results,
}

PAGES[st.session_state.page]()
