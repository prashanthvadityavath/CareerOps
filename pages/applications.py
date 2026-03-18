"""Applications: Kanban board (reuse dashboard pipeline)."""
import streamlit as st
from config import APPLICATIONS_PAGE_APPLICATIONS_KEY, PENDING_MOVES_KEY
from data.mock_data import APPLICATIONS
from components import render_kanban_card, KANBAN_COLUMNS

def _get_applications():
    if APPLICATIONS_PAGE_APPLICATIONS_KEY not in st.session_state:
        st.session_state[APPLICATIONS_PAGE_APPLICATIONS_KEY] = [a.copy() for a in APPLICATIONS]
    return st.session_state[APPLICATIONS_PAGE_APPLICATIONS_KEY]

def _apply_pending_moves(applications):
    if PENDING_MOVES_KEY not in st.session_state or not st.session_state[PENDING_MOVES_KEY]:
        return
    for app_id, target_column in st.session_state[PENDING_MOVES_KEY]:
        for app in applications:
            if app["id"] == app_id:
                app["column_id"] = target_column
                break
    st.session_state[PENDING_MOVES_KEY] = []

def render_applications():
    st.subheader("Applications")
    applications = _get_applications()
    _apply_pending_moves(applications)

    cols = st.columns(4)
    for i, (col_id, col_label) in enumerate(KANBAN_COLUMNS):
        with cols[i]:
            st.markdown(f"**{col_label}**")
            for app in applications:
                if app["column_id"] == col_id:
                    render_kanban_card(
                        app["id"], app["company"], app["role"], app["resume_tag"],
                        app["match_score"], app["date_applied"], col_id, key_suffix="app"
                    )
