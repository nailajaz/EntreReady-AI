"""EntreReady AI (ERAI) — central configuration."""

APP_TITLE = "EntreReady AI (ERAI)"
APP_SUBTITLE = ("An Explainable AI Decision Support Framework for Assessing "
                "Entrepreneurial Readiness")
PAGE_ICON = "🚀"

DISCLAIMER = (
    "ERAI indicates *current* entrepreneurial readiness and intention. "
    "It does not guarantee that a person will become an entrepreneur."
)

# --- Likert scale (replaces the raw 1-5 slider) ---
LIKERT = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

# --- Readiness bands ---
BANDS = [
    (70, "High Readiness"),
    (45, "Developing Readiness"),
    (0,  "Emerging Readiness"),
]

# --- Assessment items keyed by the SAME Qualtrics variable names ---
# (taken from your Entrepreneurial Intentions .xlsx export header)
QUESTIONS = {
    "Q.9":  "The quality of entrepreneurship education available to me is high.",
    "Q.10": "My education provided adequate resources to become an entrepreneur.",
    "Q.12": "My education is equipping me with essential entrepreneurial skills.",
    "Q28":  "Technology is important for entrepreneurship.",
    "Q29":  "Artificial Intelligence (AI) is important for entrepreneurship.",
    "Q30":  "I feel confident using Technology and AI in an entrepreneurial venture.",
}

# Feature order used by the (future) ML model
FEATURES = ["Q.9", "Q.10", "Q.12", "Q28", "Q29", "Q30"]

# --- Demographic option lists (mirror Qualtrics coding) ---
GENDER_OPTIONS = ["Female", "Male", "Prefer to self-describe", "Prefer not to say"]
EDUCATION_OPTIONS = ["High school", "Diploma", "Bachelor's", "Master's", "PhD", "Other"]
MARITAL_OPTIONS = ["Single", "Married", "Married with children", "Other"]
EXPERIENCE_OPTIONS = ["None", "Less than 1 year", "1–3 years", "3–5 years", "5+ years"]
INTEREST_OPTIONS = [
    "Technology", "Retail / E-commerce", "Food & Hospitality", "Healthcare",
    "Education", "Creative / Media", "Finance", "Social Enterprise", "Other",
]
