import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from config import (
    APP_TITLE, APP_SUBTITLE, PAGE_ICON, DISCLAIMER,
    LIKERT, QUESTIONS, FEATURES, BANDS,
    GENDER_OPTIONS, EDUCATION_OPTIONS, MARITAL_OPTIONS,
    EXPERIENCE_OPTIONS, INTEREST_OPTIONS,
)

# ---------------------------------------------------------------
# Optional trained ML model (Version 2). Falls back gracefully.
# ---------------------------------------------------------------
try:
    import joblib
    _bundle = joblib.load("models/erai_model.joblib")
    _model = _bundle["model"]
    _MODEL_FEATURES = _bundle.get("features", FEATURES)
    _HAS_MODEL = True
except Exception:
    _model, _MODEL_FEATURES, _HAS_MODEL = None, FEATURES, False

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
.hero-title { font-size: 2.4rem; font-weight: 760; margin-bottom: 0.2rem; }
.hero-subtitle { font-size: 1.05rem; color: #666; margin-bottom: 1.1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="hero-title">{PAGE_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-subtitle">{APP_SUBTITLE}</div>', unsafe_allow_html=True)

with st.expander("About this prototype"):
    st.write(
        "Version 1 uses a transparent, explainable weighted engine so the assessment "
        "flow, outputs, and recommendations can be reviewed before ML integration. "
        "When a trained model is added to /models, the app automatically switches to it."
    )

# ---------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------
def score(responses: dict):
    x = np.array([[responses[f] for f in _MODEL_FEATURES]], dtype=float)
    if _HAS_MODEL:
        proba = float(_model.predict_proba(x)[0, 1])
        overall = round(proba * 100, 1)
        conf = round(max(proba, 1 - proba) * 100, 1)
        engine = "ML model (trained on Qualtrics data)"
    else:
        overall = round((x.mean() - 1) / 4 * 100, 1)
        conf = 100.0
        engine = "Transparent weighted engine (Version 1)"
    band = next(label for cutoff, label in BANDS if overall >= cutoff)
    return overall, band, conf, engine


def likert_block(prefix=""):
    """Render all Likert items, return dict of numeric responses + label map."""
    responses, labels = {}, {}
    for var, text in QUESTIONS.items():
        choice = st.radio(text, list(LIKERT.keys()), index=2,
                          horizontal=True, key=prefix + var)
        responses[var] = LIKERT[choice]
        labels[var] = choice
    return responses, labels


def show_results(responses, labels):
    overall, band, conf, engine = score(responses)
    c1, c2, c3 = st.columns(3)
    c1.metric("ERAI Readiness Index", f"{overall}/100")
    c2.metric("Readiness Level", band)
    c3.metric("Confidence", f"{conf}%")
    st.caption(f"Engine: {engine}")

    st.subheader("Per-item responses")
    for var in FEATURES:
        st.markdown(f"- **{var}** — {QUESTIONS[var]}: *{labels[var]}* ({responses[var]}/5)")
    return overall, band, conf


# ---------------------------------------------------------------
# Mode selector
# ---------------------------------------------------------------
mode = st.sidebar.radio(
    "Choose mode",
    ["Quick Self-Assessment", "Public / Student Intake (with demographics)"],
)

# ================= MODE 1 =================
if mode == "Quick Self-Assessment":
    with st.form("erai_quick"):
        st.subheader("Quick Entrepreneurial Readiness Assessment")
        st.caption("Select the response that best reflects your current position.")
        responses, labels = likert_block(prefix="q_")
        submitted = st.form_submit_button("Generate ERAI Assessment",
                                          type="primary", use_container_width=True)
    if submitted:
        show_results(responses, labels)
        st.info(DISCLAIMER)

# ================= MODE 2 =================
else:
    with st.form("erai_intake"):
        st.subheader("Respondent Profile")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=15, max_value=90, value=22)
            gender = st.selectbox("Gender", GENDER_OPTIONS)
            education = st.selectbox("Highest level of education", EDUCATION_OPTIONS)
            marital = st.selectbox("Marital / family status", MARITAL_OPTIONS)
        with col2:
            experience = st.selectbox("Work / business experience", EXPERIENCE_OPTIONS)
            interest_area = st.selectbox("Primary interest area", INTEREST_OPTIONS)
            prior_startup = st.radio("Have you started a business before?",
                                     ["No", "Yes"], horizontal=True)
            # Independent outcome question -> Qualtrics Q.20
            plan_after_grad = st.radio(
                "Do you plan to start your own business immediately after graduation?",
                ["No", "Undecided", "Yes"], horizontal=True, key="Q.20",
            )

        st.divider()
        st.subheader("Entrepreneurial Readiness Statements")
        st.caption("Please respond to each statement.")
        responses, labels = likert_block(prefix="intake_")

        submitted = st.form_submit_button("Submit & Assess",
                                          type="primary", use_container_width=True)

    if submitted:
        overall, band, conf = show_results(responses, labels)

        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "age": age, "gender": gender, "education": education,
            "marital_status": marital, "experience": experience,
            "interest_area": interest_area, "prior_startup": prior_startup,
            "Q.20_plan_to_start": plan_after_grad,
            **{f: responses[f] for f in FEATURES},
            "readiness_index": overall, "readiness_band": band, "confidence": conf,
        }
        df_out = pd.DataFrame([record])

        st.subheader("Collected record")
        st.dataframe(df_out, use_container_width=True)

        buf = io.StringIO()
        df_out.to_csv(buf, index=False)
        st.download_button(
            "Download this response (CSV)",
            data=buf.getvalue().encode("utf-8"),
            file_name="ERAI_intake_response.csv",
            mime="text/csv", use_container_width=True,
        )
        st.info(DISCLAIMER)
