"""KPI card with optional sparkline."""
import streamlit as st
import plotly.graph_objects as go


def render_kpi_card(title: str, value, subtitle: str = "", sparkline_data=None, key_suffix: str = ""):
    """
    Render a metric card with optional tiny sparkline.
    sparkline_data: (labels, values) or None
    """
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=title, value=value, delta=subtitle)
    with col2:
        if sparkline_data:
            labels, values = sparkline_data
            fig = go.Figure(
                go.Scatter(
                    x=list(range(len(values))),
                    y=values,
                    mode="lines",
                    line=dict(color="#1e3a5f", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(30, 58, 95, 0.15)",
                )
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=50,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            fig.update_xaxes(autorange=True)
            st.plotly_chart(fig, use_container_width=True, key=f"spark_{title}_{key_suffix}")
    return None
