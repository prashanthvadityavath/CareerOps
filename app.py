"""
CareerOps – The Autonomous Career Command Center.
Entry point: sidebar nav + header + page content.
"""
import streamlit as st
from config import DAILY_APPLICATIONS_DONE_KEY
from components.header import inject_css, render_header
from data.mock_data import DAILY_APPLICATIONS_DONE, DAILY_GOAL_APPLICATIONS

# Page render functions (implemented in pages/)
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

st.set_page_config(page_title="CareerOps", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
inject_css()

with st.sidebar:
    st.markdown("## CareerOps")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
        key="main_nav",
    )

if DAILY_APPLICATIONS_DONE_KEY not in st.session_state:
    st.session_state[DAILY_APPLICATIONS_DONE_KEY] = DAILY_APPLICATIONS_DONE
render_header(daily_goal=DAILY_GOAL_APPLICATIONS)
PAGES[page]()
