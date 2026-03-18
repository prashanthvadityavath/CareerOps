"""Dashboard: KPI cards, Kanban pipeline, Activity timeline."""
import streamlit as st
from config import DASHBOARD_APPLICATIONS_KEY, PENDING_MOVES_KEY
from data.mock_data import APPLICATIONS, ACTIVITY_EVENTS, get_dashboard_kpis, get_kpi_sparkline_data
from components import render_kpi_card, render_kanban_card, KANBAN_COLUMNS, render_activity_timeline


def _get_applications():
    if DASHBOARD_APPLICATIONS_KEY not in st.session_state:
        st.session_state[DASHBOARD_APPLICATIONS_KEY] = [a.copy() for a in APPLICATIONS]
    return st.session_state[DASHBOARD_APPLICATIONS_KEY]


def _apply_pending_moves(applications):
    if PENDING_MOVES_KEY not in st.session_state or not st.session_state[PENDING_MOVES_KEY]:
        return
    for app_id, target_column in st.session_state[PENDING_MOVES_KEY]:
        for app in applications:
            if app["id"] == app_id:
                app["column_id"] = target_column
                break
    st.session_state[PENDING_MOVES_KEY] = []


def render_dashboard():
    applications = _get_applications()
    _apply_pending_moves(applications)

    kpis = get_dashboard_kpis()
    spark = get_kpi_sparkline_data()

    st.subheader("Stats overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Applications", kpis["total_applications"], "All time", spark["applications"], "apps")
    with col2:
        render_kpi_card("Interviews", kpis["interviews"], "Scheduled", spark["interviews"], "int")
    with col3:
        render_kpi_card("Offers", kpis["offers"], "Received", spark["offers"], "off")
    with col4:
        render_kpi_card("Conversion Rate", f"{kpis['conversion_rate']}%", "Application → Offer", spark["conversion"], "conv")

    st.markdown("---")
    st.subheader("Application pipeline")

    main_col, timeline_col = st.columns([3, 1])
    with main_col:
        cols = st.columns(4)
        for i, (col_id, col_label) in enumerate(KANBAN_COLUMNS):
            with cols[i]:
                st.markdown(f"**{col_label}**")
                for app in applications:
                    if app["column_id"] == col_id:
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
        st.markdown("**Activity**")
        render_activity_timeline(ACTIVITY_EVENTS, "dash")
