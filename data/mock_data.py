"""Dummy data for CareerOps dashboard. No backend."""
import pandas as pd
from datetime import datetime, timedelta

# Kanban columns
KANBAN_COLUMN_IDS = ["saved", "applied", "interviewing", "offer_rejected"]

# Application cards: dates relative to today so the demo doesn't look stale
def _relative_date(days_ago: int) -> str:
    return (datetime.now().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _relative_datetime(days_ago: int, hour: int = 12, minute: int = 0) -> str:
    d = datetime.now().date() - timedelta(days=days_ago)
    return d.strftime("%Y-%m-%d") + f" {hour:02d}:{minute:02d}"


APPLICATIONS = [
    {"id": "1", "company": "TechCorp", "role": "Data Scientist", "resume_tag": "Data Scientist v2", "match_score": 87, "date_applied": _relative_date(0), "column_id": "saved"},
    {"id": "2", "company": "DataFlow Inc", "role": "ML Engineer", "resume_tag": "ML Engineer v1", "match_score": 92, "date_applied": _relative_date(2), "column_id": "applied"},
    {"id": "3", "company": "Analytics Co", "role": "Senior Analyst", "resume_tag": "Analytics v3", "match_score": 78, "date_applied": _relative_date(5), "column_id": "interviewing"},
    {"id": "4", "company": "StartupXYZ", "role": "Backend Developer", "resume_tag": "Backend v1", "match_score": 85, "date_applied": _relative_date(8), "column_id": "offer_rejected"},
    {"id": "5", "company": "BigBank", "role": "Quant Analyst", "resume_tag": "Quant v2", "match_score": 91, "date_applied": _relative_date(1), "column_id": "saved"},
    {"id": "6", "company": "HealthTech", "role": "Data Engineer", "resume_tag": "Data Engineer v1", "match_score": 88, "date_applied": _relative_date(3), "column_id": "applied"},
]

# Activity timeline events: timestamps relative to now
ACTIVITY_EVENTS = [
    {"type": "resume_generated", "label": "Resume generated for Data Scientist at TechCorp", "timestamp": _relative_datetime(0, 14, 30)},
    {"type": "application_submitted", "label": "Application submitted to DataFlow Inc", "timestamp": _relative_datetime(1, 11, 0)},
    {"type": "interview_update", "label": "Interview scheduled with Analytics Co – Round 2", "timestamp": _relative_datetime(2, 9, 15)},
    {"type": "status_changed", "label": "StartupXYZ – moved to Offer / Rejected", "timestamp": _relative_datetime(4, 16, 45)},
    {"type": "resume_generated", "label": "Resume tailored for Quant Analyst at BigBank", "timestamp": _relative_datetime(5, 10, 0)},
    {"type": "application_submitted", "label": "Application submitted to HealthTech", "timestamp": _relative_datetime(6, 13, 20)},
]

# KPI sparkline data (last 7 days): list of (label, values) per metric
def get_kpi_sparkline_data():
    base = datetime.now().date()
    days = [(base - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    return {
        "applications": (days, [2, 1, 3, 0, 2, 1, 1]),
        "interviews": (days, [0, 1, 0, 1, 0, 1, 0]),
        "offers": (days, [0, 0, 0, 0, 1, 0, 0]),
        "conversion": (days, [0, 5, 0, 10, 15, 0, 0]),
    }

# Dashboard KPIs (totals)
def get_dashboard_kpis():
    return {
        "total_applications": 24,
        "interviews": 6,
        "offers": 2,
        "conversion_rate": 8.3,
    }

# Daily goal
DAILY_GOAL_APPLICATIONS = 5
DAILY_APPLICATIONS_DONE = 3

# Applications per week (for line chart)
def get_applications_per_week_df():
    return pd.DataFrame({
        "week": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
        "applications": [3, 5, 4, 6, 4, 2],
    })

# Resume version vs interview rate (bar chart)
def get_resume_version_interview_df():
    return pd.DataFrame({
        "version": ["Data Scientist v2", "ML Engineer v1", "Analytics v3", "Backend v1"],
        "interview_rate": [25, 40, 15, 20],
    })

# Application status distribution (pie)
def get_status_distribution():
    return pd.DataFrame({
        "status": ["Saved", "Applied", "Interviewing", "Offer", "Rejected"],
        "count": [4, 8, 5, 2, 5],
    })

# Activity heatmap: day of week x week (or simple 7x4)
def get_activity_heatmap_data():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # 4 weeks of mock counts per day
    data = [
        [2, 1, 3, 0, 2, 0, 0],
        [1, 2, 1, 2, 1, 0, 0],
        [0, 3, 2, 1, 2, 1, 0],
        [2, 0, 1, 3, 0, 0, 0],
    ]
    return days, data

# Extracted keywords (mock for Generate Resume)
EXTRACTED_KEYWORDS = ["Python", "SQL", "Machine Learning", "A/B Testing", "Data pipelines", "Tableau", "Statistics", "Collaboration"]

# Default resume preview text
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

# Master Profile mock data
MASTER_SKILLS = ["Python", "SQL", "Machine Learning", "A/B Testing", "Tableau", "R", "Statistics"]
MASTER_SKILL_CATEGORIES = ["ML", "Backend", "Analytics", "Data"]

MASTER_PROJECTS = [
    {"title": "Recommendation Engine", "description": "Collaborative filtering model for e-commerce. Python, scikit-learn.", "category": "ML"},
    {"title": "ETL Pipeline", "description": "Airflow DAGs for daily data ingestion. Python, PostgreSQL.", "category": "Backend"},
    {"title": "Dashboard Redesign", "description": "Executive dashboards in Tableau; 30% faster load.", "category": "Analytics"},
]

MASTER_EXPERIENCE = [
    {"role": "Data Analyst", "company": "ABC Corp", "start": "2022", "end": "Present"},
    {"role": "Research Assistant", "company": "University Lab", "start": "2020", "end": "2022"},
]
