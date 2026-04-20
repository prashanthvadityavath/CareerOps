"""
CareerOps – The Autonomous Career Command Center.
Entry point: page config, CSS injection, session state, nav routing.
"""
import streamlit as st
from config import (
    DAILY_APPLICATIONS_DONE_KEY,
    DAILY_GOAL_KEY,
    CURRENT_PAGE_KEY,
    DEFAULT_DAILY_GOAL,
)
from components.header import inject_css, render_header
from pages.dashboard import render_dashboard
from pages.generate_resume import render_generate_resume
from pages.applications import render_applications
from pages.analytics import render_analytics
from pages.master_profile import render_master_profile
from pages.settings import render_settings


PAGES = {
    "Dashboard": render_dashboard,
    "Generate Resume": render_generate_resume,
    "Applications": render_applications,
    "Analytics": render_analytics,
    "Master Profile": render_master_profile,
    "Settings": render_settings,
}

PAGE_ICONS = {
    "Dashboard": ":material/dashboard:",
    "Generate Resume": ":material/description:",
    "Applications": ":material/work:",
    "Analytics": ":material/insights:",
    "Master Profile": ":material/account_circle:",
    "Settings": ":material/settings:",
}

def init_session_state() -> None:
    """Initialize all required session state variables with safe defaults."""
    default_page = "Dashboard"
    if "page" in st.query_params and st.query_params["page"] in PAGES:
        default_page = st.query_params["page"]

    defaults = {
        DAILY_APPLICATIONS_DONE_KEY: 0,   # no longer seeded from mock_data
        DAILY_GOAL_KEY: DEFAULT_DAILY_GOAL,
        CURRENT_PAGE_KEY: default_page,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Keep URL in sync on first load if it was missing
    if st.query_params.get("page") != st.session_state[CURRENT_PAGE_KEY]:
        st.query_params["page"] = st.session_state[CURRENT_PAGE_KEY]


def render_nav() -> str:
    """
    Render a horizontal nav bar using styled st.columns buttons.
    Returns the name of the currently active page.
    """
    cols = st.columns(len(PAGES))
    
    cols[0].markdown("<div class='nav-marker'></div>", unsafe_allow_html=True)
    for col, name in zip(cols, PAGES):
        is_active = st.session_state[CURRENT_PAGE_KEY] == name
        label = f"**{name}**" if is_active else name
        icon = PAGE_ICONS.get(name)
        if col.button(label, icon=icon, key=f"nav_{name}", use_container_width=True):
            st.session_state[CURRENT_PAGE_KEY] = name
            st.query_params["page"] = name
            st.rerun()

    st.markdown(
        """
        <style>
        div.element-container:has(.nav-marker) {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    return st.session_state[CURRENT_PAGE_KEY]


def main() -> None:
    st.set_page_config(
        page_title="CareerOps",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    init_session_state()

    render_header(
        daily_done=st.session_state[DAILY_APPLICATIONS_DONE_KEY],
        daily_goal=st.session_state[DAILY_GOAL_KEY],
    )

    render_nav()

    current_page = st.session_state[CURRENT_PAGE_KEY]
    page_fn = PAGES.get(current_page, render_dashboard)
    page_fn()


if __name__ == "__main__":
    main()