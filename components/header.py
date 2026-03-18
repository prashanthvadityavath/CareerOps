"""Top header bar: logo, daily goal, notification, user dropdown."""
import streamlit as st
from pathlib import Path

from config import DAILY_APPLICATIONS_DONE_KEY


def inject_css():
    """Inject .streamlit/style.css if present (path relative to project root)."""
    project_root = Path(__file__).resolve().parent.parent
    css_path = project_root / ".streamlit" / "style.css"
    if css_path.is_file():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header(daily_goal: int = 5):
    """Render top header: CareerOps logo, daily goal from session state, notification button, profile dropdown."""
    daily_done = st.session_state.get(DAILY_APPLICATIONS_DONE_KEY, 0)
    c1, c2, c3, c4 = st.columns([2, 1, 0.3, 0.8])
    with c1:
        st.markdown("### CareerOps")
    with c2:
        st.markdown(f"**{daily_done}/{daily_goal} Applications Today**")
    with c3:
        if st.button("🔔", key="header_notification_btn", help="Notifications"):
            st.toast("No new notifications")
    with c4:
        profile = st.selectbox(
            "Profile",
            ["John Doe", "Settings", "Sign out"],
            label_visibility="collapsed",
            key="header_profile",
        )
        if profile == "Settings":
            st.session_state["main_nav"] = "Settings"
            st.rerun()
        if profile == "Sign out":
            st.session_state["header_profile"] = "John Doe"
            st.toast("Signed out (mock)")
            st.rerun()
    st.divider()
