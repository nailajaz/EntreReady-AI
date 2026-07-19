"""scoring.py — ERAI weighted scoring engine (Version 1)."""

DIMENSIONS = [
    {"id": "motivation",    "name": "Entrepreneurial Motivation",             "short_name": "Motivation",    "description": "Commitment, career intention, and willingness to pursue venture creation.", "weight": 0.18},
    {"id": "self_efficacy", "name": "Entrepreneurial Self-Efficacy",          "short_name": "Self-Efficacy", "description": "Confidence in planning, decision-making, leadership, and problem-solving.",  "weight": 0.20},
    {"id": "innovation",    "name": "Innovation & Opportunity Recognition",   "short_name": "Innovation",    "description": "Ability to recognize needs, generate ideas, and test new solutions.",         "weight": 0.18},
    {"id": "resilience",    "name": "Risk Management & Resilience",           "short_name": "Resilience",    "description": "Readiness to manage uncertainty, calculated risk, setbacks, and change.",     "weight": 0.16},
    {"id": "business_ai",   "name": "Business & AI Readiness",                "short_name": "Business & AI", "description": "Business knowledge, data use, digital capability, and responsible AI use.",    "weight": 0.18},
    {"id": "support",       "name": "Resources & Support",                    "short_name": "Support",       "description": "Access to networks, mentors, information, education, and other enablers.",     "weight": 0.10},
]

QUESTIONS = [
    {"id": "M1", "dimension": "motivation",    "text": "Starting or developing a venture is important to my future career."},
    {"id": "M2", "dimension": "motivation",    "text": "I am willing to invest sustained effort to build a business or venture."},
    {"id": "M3", "dimension": "motivation",    "text": "I actively look for opportunities that could become a business."},
    {"id": "S1", "dimension": "self_efficacy", "text": "I am confident that I can evaluate whether a business idea is viable."},
    {"id": "S2", "dimension": "self_efficacy", "text": "I can make decisions when business information is incomplete or uncertain."},
    {"id": "S3", "dimension": "self_efficacy", "text": "I am confident that I can organize and lead the work needed to launch a venture."},
    {"id": "I1", "dimension": "innovation",    "text": "I can identify unmet customer or community needs."},
    {"id": "I2", "dimension": "innovation",    "text": "I frequently generate practical ideas to solve real problems."},
    {"id": "I3", "dimension": "innovation",    "text": "I am willing to test and improve an idea based on feedback."},
    {"id": "R1", "dimension": "resilience",    "text": "I can manage the uncertainty and risk involved in starting a venture."},
    {"id": "R2", "dimension": "resilience",    "text": "I recover and adapt when a plan does not work as expected."},
    {"id": "R3", "dimension": "resilience",    "text": "I take calculated risks rather than avoiding them entirely."},
    {"id": "B1", "dimension": "business_ai",   "text": "I understand core business fundamentals (customers, revenue, costs)."},
    {"id": "B2", "dimension": "business_ai",   "text": "I can use data and digital tools to support business decisions."},
    {"id": "B3", "dimension": "business_ai",   "text": "I am confident using AI tools responsibly in an entrepreneurial context."},
    {"id": "P1", "dimension": "support",       "text": "I have access to mentors, networks, or information to support a venture."},
    {"id": "P2", "dimension": "support",       "text": "I can find the education or resources I need to build entrepreneurial skills."},
]


def _normalize_likert(mean_value, min_scale=1, max_scale=5):
    """Convert a 1–5 mean into a 0–100 score."""
    span = max_scale - min_scale
    if span <= 0:
        return 0.0
    return (mean_value - min_scale) / span * 100.0


def _readiness_level(overall_score):
    if overall_score < 40:
        return "Emerging"
    elif overall_score < 55:
        return "Developing"
    elif overall_score < 70:
        return "Progressing"
    elif overall_score < 85:
        return "Strong"
    return "Advanced"


def calculate_results(numeric_responses):
    """
    Compute the ERAI readiness profile.

    Parameters
    ----------
    numeric_responses : dict  {question_id: 1..5}

    Returns
    -------
    dict with keys: overall_score, readiness_level, dimension_scores,
                    strengths, gaps, interpretation
    """
    dimensions = DIMENSIONS

    # Group scores by dimension
    per_dimension = {d["id"]: [] for d in dimensions}
    for q in QUESTIONS:
        qid = q["id"]
        dim = q["dimension"]
        if qid in numeric_responses and dim in per_dimension:
            per_dimension[dim].append(numeric_responses[qid])

    # Mean → 0–100 per dimension
    dimension_scores = {}
    for dimension in dimensions:
        values = per_dimension[dimension["id"]]
        if not values:
            dimension_scores[dimension["id"]] = 0.0
            continue
        mean_value = sum(values) / len(values)
        dimension_scores[dimension["id"]] = round(_normalize_likert(mean_value), 2)

    # Weighted overall (self-normalizing by weight_total)
    weight_total = sum(float(d["weight"]) for d in dimensions)
    overall_score = sum(
        dimension_scores[d["id"]] * float(d["weight"]) for d in dimensions
    ) / weight_total
    overall_score = round(overall_score, 2)

    # Rank → top 2 strengths, bottom 2 gaps
    ranked = sorted(
        [
            {"id": d["id"], "name": d["name"], "score": dimension_scores[d["id"]]}
            for d in dimensions
        ],
        key=lambda item: item["score"],
        reverse=True,
    )
    strengths = ranked[:2]
    gaps = sorted(ranked[-2:], key=lambda item: item["score"])

    # Interpretation bands (from the PDF)
    if overall_score < 40:
        interpretation = (
            "Your current profile suggests that foundational entrepreneurial "
            "capabilities and support systems should be developed before "
            "substantial venture commitments are made."
        )
    elif overall_score < 55:
        interpretation = (
            "You show initial entrepreneurial potential, but several important "
            "capabilities require structured development."
        )
    elif overall_score < 70:
        interpretation = (
            "You demonstrate developing entrepreneurial readiness, with a "
            "balanced base that can be strengthened through targeted practice "
            "and support."
        )
    elif overall_score < 85:
        interpretation = (
            "You demonstrate strong entrepreneurial readiness and appear "
            "prepared to advance a business idea through structured validation "
            "and planning."
        )
    else:
        interpretation = (
            "You demonstrate advanced entrepreneurial readiness across most "
            "assessed dimensions. The next priority is disciplined execution, "
            "validation, and responsible scaling."
        )

    return {
        "overall_score": overall_score,
        "readiness_level": _readiness_level(overall_score),
        "dimension_scores": dimension_scores,
        "strengths": strengths,
        "gaps": gaps,
        "interpretation": interpretation,
    }
