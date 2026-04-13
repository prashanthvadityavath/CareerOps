"""Dashboard: KPI summary, application pipeline, activity timeline."""
import streamlit as st
from config import DASHBOARD_APPLICATIONS_KEY, PENDING_MOVES_KEY
from data.mock_data import (
    APPLICATIONS,
    ACTIVITY_EVENTS,
    get_dashboard_kpis,
    get_kpi_sparkline_data,
)
from components import (
    render_kpi_card,
    render_kanban_card,
    render_activity_timeline,
    KANBAN_COLUMNS,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_applications() -> list:
    if DASHBOARD_APPLICATIONS_KEY not in st.session_state:
        st.session_state[DASHBOARD_APPLICATIONS_KEY] = [
            a.copy() for a in APPLICATIONS
        ]
    return st.session_state[DASHBOARD_APPLICATIONS_KEY]


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

def render_dashboard() -> None:
    applications = _get_applications()
    _apply_pending_moves(applications)

    kpis = get_dashboard_kpis()
    spark = get_kpi_sparkline_data()

    # ── Page header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 1rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Dashboard
            </p>
            <p style="font-size:13px; color:rgba(128,128,128,0.85); margin:4px 0 0;">
                Your job search at a glance
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            "Total Applications",
            kpis["total_applications"],
            "All time",
            spark["applications"],
            "apps",
        )
    with k2:
        render_kpi_card(
            "Interviews",
            kpis["interviews"],
            "Scheduled",
            spark["interviews"],
            "int",
        )
    with k3:
        render_kpi_card(
            "Offers",
            kpis["offers"],
            "Received",
            spark["offers"],
            "off",
        )
    with k4:
        render_kpi_card(
            "Conversion Rate",
            f"{kpis['conversion_rate']}%",
            "Application to offer",
            spark["conversion"],
            "conv",
        )

    st.markdown(
        "<div style='height:1px; background:rgba(128,128,128,0.15); margin:1.5rem 0;'></div>",
        unsafe_allow_html=True,
    )

    # ── Pipeline + timeline ──────────────────────────────────────
    pipeline_col, timeline_col = st.columns([3, 1])

    with pipeline_col:
        st.markdown(
            "<p style='font-size:14px; font-weight:600; margin-bottom:12px;'>Application pipeline</p>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(KANBAN_COLUMNS))
        for i, (col_id, col_label) in enumerate(KANBAN_COLUMNS):
            col_apps = [a for a in applications if a["column_id"] == col_id]
            with cols[i]:
                st.markdown(
                    f"""
                    <div style='display:flex; align-items:center; gap:8px; margin-bottom:10px;'>
                        <span style='font-size:13px; font-weight:500;'>{col_label}</span>
                        <span style='
                            font-size:11px;
                            font-weight:500;
                            padding:1px 7px;
                            border-radius:10px;
                            border:1px solid rgba(128,128,128,0.2);
                            color:rgba(128,128,128,0.85);
                        '>{len(col_apps)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                for app in col_apps:
                    render_kanban_card(
                        app["id"],
                        app["company"],
                        app["role"],
                        app["resume_tag"],
                        app["match_score"],
                        app["date_applied"],
                        col_id,
                        key_suffix="dash",
                    )

    with timeline_col:
        st.markdown(
            "<p style='font-size:14px; font-weight:600; margin-bottom:12px;'>Recent activity</p>",
            unsafe_allow_html=True,
        )
        render_activity_timeline(ACTIVITY_EVENTS, "dash")