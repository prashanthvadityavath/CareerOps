"""Dashboard: KPI summary, application pipeline, activity timeline."""
import streamlit as st
from data.db_utils import get_applications, get_activity_timeline
from data.mock_data import get_kpi_sparkline_data
from components import (
    render_kpi_card,
    render_kanban_card,
    render_activity_timeline,
    KANBAN_COLUMNS,
)


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render_dashboard() -> None:
    active_id = st.session_state.get("active_candidate_id")
    if not active_id:
        st.info("Select a candidate to view the dashboard.")
        return
        
    applications = get_applications(active_id)
    activities = get_activity_timeline(active_id)

    total_apps = len(applications)
    interviews = len([a for a in applications if a['column_id'] == 'interviewing'])
    offers = len([a for a in applications if a['column_id'] == 'offer_rejected'])
    conversion_rate = round((offers / total_apps * 100), 1) if total_apps > 0 else 0.0

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
            total_apps,
            "All time",
            spark["applications"],
            "apps",
        )
    with k2:
        render_kpi_card(
            "Interviews",
            interviews,
            "Scheduled",
            spark["interviews"],
            "int",
        )
    with k3:
        render_kpi_card(
            "Offers",
            offers,
            "Received",
            spark["offers"],
            "off",
        )
    with k4:
        render_kpi_card(
            "Conversion Rate",
            f"{conversion_rate}%",
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
        render_activity_timeline(activities, "dash")