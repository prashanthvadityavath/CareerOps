"""
Mock data for CareerOps.
Used by: Dashboard, Applications, Analytics, Generate Resume.
Master Profile reads from PostgreSQL — no mock data needed there.
"""
import pandas as pd
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _relative_date(days_ago: int) -> str:
    return (datetime.now().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _relative_datetime(days_ago: int, hour: int = 12, minute: int = 0) -> str:
    d = datetime.now().date() - timedelta(days=days_ago)
    return d.strftime("%b %d") + f" at {hour:02d}:{minute:02d}"


# ---------------------------------------------------------------------------
# Kanban applications
# ---------------------------------------------------------------------------

APPLICATIONS = [
    {
        "id": "1",
        "company": "TechCorp",
        "role": "Data Scientist",
        "resume_tag": "Data Scientist v2",
        "match_score": 87,
        "date_applied": _relative_date(0),
        "column_id": "saved",
    },
    {
        "id": "2",
        "company": "DataFlow Inc",
        "role": "ML Engineer",
        "resume_tag": "ML Engineer v1",
        "match_score": 92,
        "date_applied": _relative_date(2),
        "column_id": "applied",
    },
    {
        "id": "3",
        "company": "Analytics Co",
        "role": "Senior Analyst",
        "resume_tag": "Analytics v3",
        "match_score": 78,
        "date_applied": _relative_date(5),
        "column_id": "interviewing",
    },
    {
        "id": "4",
        "company": "StartupXYZ",
        "role": "Backend Developer",
        "resume_tag": "Backend v1",
        "match_score": 85,
        "date_applied": _relative_date(8),
        "column_id": "offer_rejected",
    },
    {
        "id": "5",
        "company": "BigBank",
        "role": "Quant Analyst",
        "resume_tag": "Quant v2",
        "match_score": 91,
        "date_applied": _relative_date(1),
        "column_id": "saved",
    },
    {
        "id": "6",
        "company": "HealthTech",
        "role": "Data Engineer",
        "resume_tag": "Data Engineer v1",
        "match_score": 88,
        "date_applied": _relative_date(3),
        "column_id": "applied",
    },
]


# ---------------------------------------------------------------------------
# Activity timeline
# ---------------------------------------------------------------------------

ACTIVITY_EVENTS = [
    {
        "type": "resume_generated",
        "label": "Resume generated for Data Scientist at TechCorp",
        "timestamp": _relative_datetime(0, 14, 30),
    },
    {
        "type": "application_submitted",
        "label": "Application submitted to DataFlow Inc",
        "timestamp": _relative_datetime(1, 11, 0),
    },
    {
        "type": "interview_update",
        "label": "Interview scheduled with Analytics Co — Round 2",
        "timestamp": _relative_datetime(2, 9, 15),
    },
    {
        "type": "status_changed",
        "label": "StartupXYZ moved to Offer / Rejected",
        "timestamp": _relative_datetime(4, 16, 45),
    },
    {
        "type": "resume_generated",
        "label": "Resume tailored for Quant Analyst at BigBank",
        "timestamp": _relative_datetime(5, 10, 0),
    },
    {
        "type": "application_submitted",
        "label": "Application submitted to HealthTech",
        "timestamp": _relative_datetime(6, 13, 20),
    },
]


# ---------------------------------------------------------------------------
# KPIs and sparklines
# ---------------------------------------------------------------------------

def get_dashboard_kpis() -> dict:
    return {
        "total_applications": 24,
        "interviews": 6,
        "offers": 2,
        "conversion_rate": 8.3,
    }


def get_kpi_sparkline_data() -> dict:
    base = datetime.now().date()
    days = [(base - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    return {
        "applications": (days, [2, 1, 3, 0, 2, 1, 1]),
        "interviews":   (days, [0, 1, 0, 1, 0, 1, 0]),
        "offers":       (days, [0, 0, 0, 0, 1, 0, 0]),
        "conversion":   (days, [0, 5, 0, 10, 15, 0, 0]),
    }


# ---------------------------------------------------------------------------
# Analytics charts
# ---------------------------------------------------------------------------

def get_applications_per_week_df() -> pd.DataFrame:
    return pd.DataFrame({
        "week":         ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
        "applications": [3, 5, 4, 6, 4, 2],
    })


def get_resume_version_interview_df() -> pd.DataFrame:
    return pd.DataFrame({
        "version":       ["Data Scientist v2", "ML Engineer v1", "Analytics v3", "Backend v1"],
        "interview_rate": [25, 40, 15, 20],
    })


def get_status_distribution() -> pd.DataFrame:
    return pd.DataFrame({
        "status": ["Saved", "Applied", "Interviewing", "Offer", "Rejected"],
        "count":  [4, 8, 5, 2, 5],
    })


def get_activity_heatmap_data() -> tuple[list, list]:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    data = [
        [2, 1, 3, 0, 2, 0, 0],
        [1, 2, 1, 2, 1, 0, 0],
        [0, 3, 2, 1, 2, 1, 0],
        [2, 0, 1, 3, 0, 0, 0],
    ]
    return days, data


# ---------------------------------------------------------------------------
# Generate Resume page
# ---------------------------------------------------------------------------

EXTRACTED_KEYWORDS = [
    "Python", "SQL", "Machine Learning", "A/B Testing",
    "Data pipelines", "Tableau", "Statistics", "Collaboration",
]

DEFAULT_RESUME_PREVIEW = """# John Doe
Data Scientist | New York, NY

## Experience
**Data Analyst**, ABC Corp (2022 – Present)
- Built predictive models; improved conversion by 15%.
- Led A/B tests and data pipelines in Python and SQL.

**Research Assistant**, University Lab (2020 – 2022)
- ML experiments; published 2 papers.

## Skills
Python, SQL, R, Machine Learning, Statistics, Tableau
"""