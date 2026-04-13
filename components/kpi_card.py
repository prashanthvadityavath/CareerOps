"""KPI metric card with optional sparkline."""
import streamlit as st
import plotly.graph_objects as go


def render_kpi_card(
    title: str,
    value,
    subtitle: str = "",
    sparkline_data=None,
    key_suffix: str = "",
) -> None:
    """
    Render a bordered metric card with label, value, subtitle, and
    an optional sparkline. Uses CSS variables so it works in both
    light and dark mode.
    """
    spark_html = ""
    if sparkline_data:
        labels, values = sparkline_data
        fig = go.Figure(
            go.Scatter(
                x=list(range(len(values))),
                y=values,
                mode="lines",
                line=dict(color="#185FA5", width=1.5),
                fill="tozeroy",
                fillcolor="rgba(24, 95, 165, 0.08)",
            )
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=40,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )

    st.markdown(
        f"""
        <div class="kpi-card">
            <p style="
                font-size: 11px;
                font-weight: 500;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                opacity: 0.5;
                margin: 0 0 6px;
            ">{title}</p>
            <p style="
                font-size: 28px;
                font-weight: 600;
                margin: 0 0 4px;
                line-height: 1;
            ">{value}</p>
            <p style="
                font-size: 12px;
                opacity: 0.5;
                margin: 0;
            ">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if sparkline_data:
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"spark_{title}_{key_suffix}",
            config={"displayModeBar": False},
        )