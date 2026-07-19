import numpy as np
import streamlit as st

# --- optional: load trained model if present, else use transparent weights ---
try:
    import joblib
    _bundle = joblib.load("models/erai_model.joblib")
    _model, _FEATURES = _bundle["model"], _bundle["features"]
    _HAS_MODEL = True
except Exception:
    _model, _HAS_MODEL = None, False
    _FEATURES = ["Q.9", "Q.10", "Q.12", "Q28", "Q29", "Q30"]

st.set_page_config(page_title="EntreReady AI (ERAI)", page_icon="🚀", layout="wide")

st.markdown("<h1>🚀 EntreReady AI (ERAI)</h1>", unsafe_allow_html=True)
st.caption("Explainable AI Decision Support for Entrepreneurial Readiness")

# Questions keyed by the SAME Qualtrics variable names
QUESTIONS = {
    "Q.9":  "How would you rate the quality of entrepreneurship education at your institution?",
    "Q.10": "Did your education provide adequate resources to become an entrepreneur?",
    "Q.12": "Is your education equipping you with essential entrepreneurial skills?",
    "Q28":  "How important is Technology for entrepreneurship?",
    "Q29":  "How important is AI for entrepreneurship?",
    "Q30":  "How confident are you using Technology and AI in your venture?",
}

with st.form("erai"):
    responses = {}
    for var, text in QUESTIONS.items():
        responses[var] = st.slider(f"{text}  ({var})", 1, 5, 3)
    submitted = st.form_submit_button("Generate ERAI Assessment",
                                      type="primary", use_container_width=True)

if submitted:
    x = np.array([[responses[f] for f in _FEATURES]], dtype=float)

    if _HAS_MODEL:
        proba = float(_model.predict_proba(x)[0, 1])
        overall = round(proba * 100, 1)
        conf = round(max(proba, 1 - proba) * 100, 1)
        engine = "ML model (trained on Qualtrics data)"
    else:
        overall = round((x.mean() - 1) / 4 * 100, 1)   # transparent weighted fallback
        conf = 100.0
        engine = "Transparent weighted engine (Version 1)"

    band = ("High Readiness" if overall >= 70
            else "Developing Readiness" if overall >= 45
            else "Emerging Readiness")

    c1, c2, c3 = st.columns(3)
    c1.metric("ERAI Readiness Index", f"{overall}/100")
    c2.metric("Readiness Level", band)
    c3.metric("Confidence", f"{conf}%")
    st.caption(f"Engine: {engine}")

    st.subheader("Per-item scores")
    for f in _FEATURES:
        st.markdown(f"- **{f}** — {QUESTIONS[f]}: {responses[f]}/5")

st.info("This tool indicates *current* entrepreneurial readiness — it does not "
        "predict that a person will definitely become an entrepreneur.")
