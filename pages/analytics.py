"""Analytics: application trends, resume performance, status breakdown, activity heatmap."""
import streamlit as st
import pandas as pd
from data.db_utils import get_applications
from data.mock_data import (
    get_applications_per_week_df,
    get_activity_heatmap_data,
)
from components import (
    applications_per_week_chart,
    resume_version_interview_chart,
    status_distribution_chart,
    activity_heatmap_chart,
)

_CHART_CFG = {"displayModeBar": False}


def render_analytics() -> None:
    active_id = st.session_state.get("active_candidate_id")
    if not active_id:
        st.info("Select a candidate to view analytics.")
        return

    applications = get_applications(active_id)
    df = pd.DataFrame(applications)

    # ── Page header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 1.25rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Analytics
            </p>
            <p style="font-size:13px; opacity:0.5; margin:4px 0 0;">
                Trends and patterns across your job search
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No applications logged yet. Save applications in the 'Generate Resume' tab to view analytics.")
        return

    # Prepare status distribution
    status_counts = df['column_id'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    status_counts['status'] = status_counts['status'].str.replace('_', ' ').str.title()

    # Prepare resume version interview rate
    version_counts = df.groupby('resume_tag').apply(
        lambda x: (x['column_id'] == 'interviewing').sum() / len(x) * 100
    ).reset_index()
    version_counts.columns = ['version', 'interview_rate']
    version_counts['interview_rate'] = version_counts['interview_rate'].round(1)

    # ── Full-width: applications per week ────────────────────────
    st.plotly_chart(
        applications_per_week_chart(get_applications_per_week_df()),
        use_container_width=True,
        config=_CHART_CFG,
    )

    st.markdown(
        "<div style='height:1px; background:rgba(128,128,128,0.12); margin:0.5rem 0 1rem;'></div>",
        unsafe_allow_html=True,
    )

    # ── Two-column: bar + donut ──────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            resume_version_interview_chart(version_counts),
            use_container_width=True,
            config=_CHART_CFG,
        )
    with c2:
        st.plotly_chart(
            status_distribution_chart(status_counts),
            use_container_width=True,
            config=_CHART_CFG,
        )

    st.markdown(
        "<div style='height:1px; background:rgba(128,128,128,0.12); margin:0.5rem 0 1rem;'></div>",
        unsafe_allow_html=True,
    )

    # ── Full-width: activity heatmap ─────────────────────────────
    days, heatmap_data = get_activity_heatmap_data()
    st.plotly_chart(
        activity_heatmap_chart(days, heatmap_data),
        use_container_width=True,
        config=_CHART_CFG,
    )