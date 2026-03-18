"""Analytics: Line, bar, pie, heatmap charts (mock data)."""
import streamlit as st
from data.mock_data import (
    get_applications_per_week_df,
    get_resume_version_interview_df,
    get_status_distribution,
    get_activity_heatmap_data,
)
from components import (
    applications_per_week_chart,
    resume_version_interview_chart,
    status_distribution_chart,
    activity_heatmap_chart,
)

def render_analytics():
    st.subheader("Analytics")

    df_week = get_applications_per_week_df()
    st.plotly_chart(applications_per_week_chart(df_week), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        df_bar = get_resume_version_interview_df()
        st.plotly_chart(resume_version_interview_chart(df_bar), use_container_width=True)
    with c2:
        df_pie = get_status_distribution()
        st.plotly_chart(status_distribution_chart(df_pie), use_container_width=True)

    days, heatmap_data = get_activity_heatmap_data()
    st.plotly_chart(activity_heatmap_chart(days, heatmap_data), use_container_width=True)
