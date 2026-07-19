# ── Branding ────────────────────────────────────────────────
APP_TITLE = "EntreReady AI"
APP_SUBTITLE = "Entrepreneurial Readiness Assessment"
PAGE_ICON = "🚀"

DISCLAIMER = (
    "EntreReady AI provides an indicative readiness profile for educational "
    "and self-development purposes only. It is not financial, legal, or "
    "professional business advice."
)

# ── Likert scale (replaces the old sliding scale) ───────────
LIKERT_OPTIONS = [
    "Strongly disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly agree",
]

# Numeric weight for each Likert option (used by scoring.py)
LIKERT_SCORES = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

# ── Demographics (independent features) ─────────────────────
# Collected on intake; Q20 (plan to start a business) is the target variable.
DEMOGRAPHICS = [
    {"key": "age", "label": "How old are you?",
     "type": "select",
     "options": ["Under 18", "18–24", "25–34", "35–44", "45–54", "55+"]},
    {"key": "education", "label": "What is your highest level of education?",
     "type": "select",
     "options": ["High school", "Diploma", "Bachelor's", "Master's", "Doctorate", "Other"]},
    {"key": "experience", "label": "Years of work/business experience",
     "type": "select",
     "options": ["None", "Less than 1 year", "1–3 years", "4–6 years", "7+ years"]},
    {"key": "interest_area", "label": "Primary area of interest",
     "type": "select",
     "options": ["Technology", "Retail/E-commerce", "Health", "Education",
                 "Finance", "Creative/Media", "Social enterprise", "Other"]},
    {"key": "family_status", "label": "Family / marital status",
     "type": "select",
     "options": ["Single", "Married", "Partnered", "With dependents", "Prefer not to say"]},
]

# ── Assessment questions (6 readiness dimensions) ───────────
# Mapped to your Qualtrics items where applicable.
QUESTIONS = [
    # Motivation & Intention
    {"id": "Q7",  "dimension": "Motivation",   "text": "I am strongly motivated to start my own business or side hustle."},
    {"id": "Q20", "dimension": "Motivation",   "text": "I plan to start my own business immediately after graduation."},
    # Mindset
    {"id": "Q10", "dimension": "Mindset",      "text": "Seeing successful entrepreneurs inspires me to become one."},
    {"id": "M2",  "dimension": "Mindset",      "text": "I am comfortable taking calculated risks to pursue an opportunity."},
    # Skills
    {"id": "Q12", "dimension": "Skills",       "text": "I possess the core skills needed to run a business."},
    {"id": "Q14", "dimension": "Skills",       "text": "My education is equipping me with entrepreneurial skills."},
    # Education & Resources
    {"id": "Q.9", "dimension": "Education",    "text": "My education provided adequate resources to become an entrepreneur."},
    {"id": "Q11", "dimension": "Education",    "text": "The entrepreneurship education available to me is high quality."},
    # Technology & AI Readiness
    {"id": "Q28", "dimension": "Technology",   "text": "Technology is important for my entrepreneurial success."},
    {"id": "Q29", "dimension": "Technology",   "text": "I am confident using technology and AI in my venture."},
    # Resilience / Barriers
    {"id": "Q22", "dimension": "Resilience",   "text": "I have a clear plan to overcome the barriers I face."},
    {"id": "R2",  "dimension": "Resilience",   "text": "I can persevere through setbacks when building a business."},
]
INTEREST_OPTIONS = [
    "Technology", "Retail / E-commerce", "Food & Hospitality", "Healthcare",
    "Education", "Creative / Media", "Finance", "Social Enterprise", "Other",
]
