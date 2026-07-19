# reporting.py
"""
Generates a personalized, downloadable PDF report at the end of an
ERAI assessment. Next-steps content adapts to user mode:
    - "Student": co-program, capstone, campus clubs/events
    - "Public":  further training (AI/tech), incubators, mentorship/funding
"""
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
)


# --- Next-steps content, keyed by mode ---------------------------------
STUDENT_STEPS = [
    "Join the Entrepreneurial Co-Program (co-op / co-curricular track) to gain "
    "structured, mentored exposure to real venture building.",
    "Enroll in the Capstone Project so you graduate with hands-on experience of "
    "taking an idea from concept to a working prototype or pitch.",
    "Join an entrepreneurship club or student organization at your institution "
    "to build a peer network and accountability.",
    "Attend guest-speaker sessions, hackathons, and business-plan competitions "
    "to test ideas and meet potential co-founders and mentors.",
    "Use your institution's career and innovation office to find internships "
    "with startups in your area of interest.",
]

PUBLIC_STEPS = [
    "Take your training further with focused upskilling — especially AI and "
    "digital-tools courses that strengthen your venture's competitiveness.",
    "Apply to a startup incubator or accelerator to access workspace, "
    "structured programs, and investor networks.",
    "Find a mentor through local entrepreneurship networks or online "
    "communities to shorten your learning curve.",
    "Explore seed funding, grants, and pitch competitions relevant to your "
    "industry and region.",
    "Validate your idea with a small pilot or MVP before committing "
    "significant capital.",
]


def _steps_for(mode: str):
    return STUDENT_STEPS if str(mode).strip().lower().startswith("student") else PUBLIC_STEPS


def build_report_pdf(
    mode: str,
    readiness_score: float,
    readiness_level: str,
    dimension_scores: dict | None = None,
    gaps: list[str] | None = None,
    user_name: str = "",
) -> bytes:
    """
    Returns the PDF as bytes, ready for st.download_button.

    dimension_scores: {"Motivation": 4.1, "Self-Efficacy": 3.4, ...}
    gaps:             ["Business & Digital Readiness", ...]  (lowest dimensions)
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ERAITitle", parent=styles["Title"], fontSize=20, spaceAfter=6,
        textColor=colors.HexColor("#1f3b73"),
    ))
    styles.add(ParagraphStyle(
        "ERAISub", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#555555"), spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        "ERAIH2", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#1f3b73"), spaceBefore=12, spaceAfter=4,
    ))
    body = styles["BodyText"]

    story = []

    # --- Header ---
    story.append(Paragraph("ERAI Readiness Report", styles["ERAITitle"]))
    who = f"Prepared for: {user_name}  |  " if user_name else ""
    story.append(Paragraph(
        f"{who}Mode: {mode}  |  "
        f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
        styles["ERAISub"],
    ))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 10))

    # --- Score summary ---
    story.append(Paragraph("Your Readiness Result", styles["ERAIH2"]))
    story.append(Paragraph(
        f"<b>ERAI Readiness Index (ERI):</b> {readiness_score:.0f} / 100"
        f" &nbsp;&nbsp; <b>Level:</b> {readiness_level}",
        body,
    ))
    story.append(Spacer(1, 6))

    # --- Dimension breakdown ---
    if dimension_scores:
        story.append(Paragraph("Dimension Breakdown", styles["ERAIH2"]))
        items = [
            ListItem(Paragraph(f"{k}: {v:.1f} / 5", body))
            for k, v in dimension_scores.items()
        ]
        story.append(ListFlowable(items, bulletType="bullet"))
        story.append(Spacer(1, 6))

    # --- Development gaps ---
    if gaps:
        story.append(Paragraph("Development Gaps to Address", styles["ERAIH2"]))
        story.append(ListFlowable(
            [ListItem(Paragraph(g, body)) for g in gaps],
            bulletType="bullet",
        ))
        story.append(Spacer(1, 6))

    # --- Personalized next steps (mode-dependent) ---
    heading = ("Recommended Next Steps for Students"
               if _steps_for(mode) is STUDENT_STEPS
               else "Recommended Next Steps")
    story.append(Paragraph(heading, styles["ERAIH2"]))
    story.append(ListFlowable(
        [ListItem(Paragraph(s, body)) for s in _steps_for(mode)],
        bulletType="1",  # numbered
    ))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd")))
    story.append(Paragraph(
        "Generated by ERAI — Explainable AI Decision Support for Entrepreneurial Readiness.",
        styles["ERAISub"],
    ))

    doc.build(story)
    return buf.getvalue()
