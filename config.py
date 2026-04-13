"""Centralized session state and app configuration keys for CareerOps."""

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
CURRENT_PAGE_KEY = "current_page"

# ---------------------------------------------------------------------------
# Header / Daily Goal
# ---------------------------------------------------------------------------
DAILY_APPLICATIONS_DONE_KEY = "daily_applications_done"
DAILY_GOAL_KEY = "daily_goal"
DEFAULT_DAILY_GOAL = 5  # default target applications per day

# ---------------------------------------------------------------------------
# Kanban
# ---------------------------------------------------------------------------
PENDING_MOVES_KEY = "kanban_pending_moves"

# ---------------------------------------------------------------------------
# Applications (separate copies for Dashboard vs Applications page)
# ---------------------------------------------------------------------------
DASHBOARD_APPLICATIONS_KEY = "dashboard_applications"
APPLICATIONS_PAGE_APPLICATIONS_KEY = "applications_page_applications"