from reporting import build_report_pdf

pdf_bytes = build_report_pdf(
    mode=mode,                       # "Student" or "Public"
    readiness_score=eri_score,       # 0–100
    readiness_level=readiness_level, # e.g. "Developing"
    dimension_scores=dimension_scores,
    gaps=development_gaps,           # your lowest 1–2 dimensions
    user_name=user_name,             # optional, from intake form
)

st.download_button(
    label="📄 Download my ERAI Readiness Report (PDF)",
    data=pdf_bytes,
    file_name="ERAI_Readiness_Report.pdf",
    mime="application/pdf",
)
