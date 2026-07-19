# Mode-aware next steps, mapped to your survey items.
# Student paths reference: Entrepreneurial Co-Program, Capstone,
# campus clubs (Q.16), guest speakers / competitions (Q.17).
# Public paths reference: AI/tech upskilling, incubator/accelerator,
# mentorship & seed-funding networks.

STUDENT_ACTIONS = {
    "high": [
        "Apply to the **Entrepreneurial Co-Program** to formalize your venture.",
        "Use your **Capstone Project** to build and pilot your business idea.",
        "Pitch at campus **business-plan competitions** and guest-speaker events (Q.17).",
    ],
    "medium": [
        "Join a campus **entrepreneurship club or organization** (Q.16) to build your network.",
        "Attend **entrepreneur guest-speaker sessions** to close knowledge gaps (Q.17).",
        "Enroll in additional **entrepreneurship coursework** offered by your institution.",
    ],
    "low": [
        "Start with an **introductory entrepreneurship course** to build fundamentals.",
        "Explore campus **entrepreneurship clubs** (Q.16) in a low-pressure way.",
        "Meet with a **faculty mentor or career advisor** to map next steps.",
    ],
}

PUBLIC_ACTIONS = {
    "high": [
        "Apply to a **startup incubator or accelerator** to scale your venture.",
        "Connect with **mentorship and seed-funding networks** to secure capital.",
        "Deepen your edge with advanced **AI/technology upskilling** training.",
    ],
    "medium": [
        "Enroll in **AI and technology upskilling** to strengthen execution.",
        "Seek a **mentor** through professional entrepreneurship networks.",
        "Validate your idea in a **pre-accelerator or startup bootcamp**.",
    ],
    "low": [
        "Begin with **foundational AI/tech skills** training to build confidence.",
        "Join a **local entrepreneurship community** for support and mentorship.",
        "Research **incubator programs** you can grow into over the next 6–12 months.",
    ],
}


def _band(score):
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def build_recommendations(dimension_scores, mode):
    """Return development gaps + mode-aware next steps."""
    # Identify weakest dimensions as "gaps"
    gaps = []
    for dimension, score in sorted(dimension_scores.items(), key=lambda x: x[1]):
        if score < 60:
            gaps.append(
                {
                    "dimension": dimension,
                    "message": f"Scored {round(score)}%. Focus development here to raise your overall readiness.",
                }
            )
    if not gaps:
        gaps.append(
            {
                "dimension": "Overall",
                "message": "No major weak areas detected. Focus on scaling your strengths.",
            }
        )

    overall = sum(dimension_scores.values()) / len(dimension_scores)
    band = _band(overall)

    actions = STUDENT_ACTIONS[band] if mode == "Student" else PUBLIC_ACTIONS[band]

    return {"gaps": gaps[:3], "actions": actions}
