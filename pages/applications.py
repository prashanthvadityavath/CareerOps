"""Applications: full Kanban board for tracking job applications."""
import streamlit as st
from config import APPLICATIONS_PAGE_APPLICATIONS_KEY, PENDING_MOVES_KEY
from data.mock_data import APPLICATIONS
from components import render_kanban_card, KANBAN_COLUMNS


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_applications() -> list:
    if APPLICATIONS_PAGE_APPLICATIONS_KEY not in st.session_state:
        st.session_state[APPLICATIONS_PAGE_APPLICATIONS_KEY] = [
            a.copy() for a in APPLICATIONS
        ]
    return st.session_state[APPLICATIONS_PAGE_APPLICATIONS_KEY]


def _apply_pending_moves(applications: list) -> None:
    pending = st.session_state.get(PENDING_MOVES_KEY, [])
    if not pending:
        return
    move_map = {app_id: col for app_id, col in pending}
    for app in applications:
        if app["id"] in move_map:
            app["column_id"] = move_map[app["id"]]
    st.session_state[PENDING_MOVES_KEY] = []


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render_applications() -> None:
    applications = _get_applications()
    _apply_pending_moves(applications)

    # ── Page header ──────────────────────────────────────────────
    total = len(applications)
    st.markdown(
        f"""
        <div style="padding: 1.5rem 0 1.25rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Applications
            </p>
            <p style="font-size:13px; opacity:0.5; margin:4px 0 0;">
                {total} application{"s" if total != 1 else ""} tracked
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Kanban columns ───────────────────────────────────────────
    cols = st.columns(len(KANBAN_COLUMNS))
    for i, (col_id, col_label) in enumerate(KANBAN_COLUMNS):
        col_apps = [a for a in applications if a["column_id"] == col_id]
        with cols[i]:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="font-size:13px; font-weight:500;">{col_label}</span>
                    <span style="
                        font-size:11px;
                        font-weight:500;
                        padding:1px 7px;
                        border-radius:10px;
                        border:1px solid rgba(128,128,128,0.2);
                        opacity:0.65;
                    ">{len(col_apps)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if not col_apps:
                st.markdown(
                    """
                    <div style="
                        border: 1px dashed rgba(128,128,128,0.25);
                        border-radius: 8px;
                        padding: 20px 12px;
                        text-align: center;
                        font-size: 12px;
                        opacity: 0.4;
                    ">No applications</div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                for app in col_apps:
                    render_kanban_card(
                        app["id"],
                        app["company"],
                        app["role"],
                        app["resume_tag"],
                        app["match_score"],
                        app["date_applied"],
                        col_id,
                        key_suffix="app",
                    )