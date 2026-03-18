"""Chart helpers – Plotly figures from mock data."""
import pandas as pd
import plotly.graph_objects as go


def applications_per_week_chart(df: pd.DataFrame):
    fig = go.Figure(
        go.Scatter(
            x=df["week"],
            y=df["applications"],
            mode="lines+markers",
            line=dict(color="#1e3a5f", width=2),
            marker=dict(size=10),
        )
    )
    fig.update_layout(
        title="Applications per week",
        margin=dict(l=40, r=20, t=40, b=40),
        height=280,
        xaxis_title="Week",
        yaxis_title="Applications",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
    )
    return fig


def resume_version_interview_chart(df: pd.DataFrame):
    fig = go.Figure(
        go.Bar(
            x=df["version"],
            y=df["interview_rate"],
            marker_color="#1e3a5f",
            text=df["interview_rate"],
            texttemplate="%{text}%",
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Resume version vs interview rate",
        margin=dict(l=40, r=20, t=40, b=100),
        height=280,
        xaxis_title="Resume version",
        yaxis_title="Interview rate (%)",
        xaxis_tickangle=-35,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def status_distribution_chart(df: pd.DataFrame):
    fig = go.Figure(
        go.Pie(
            labels=df["status"],
            values=df["count"],
            hole=0.45,
            marker=dict(colors=["#1e3a5f", "#3d5a80", "#5c7caf", "#7eb4e8", "#98c1e8"]),
            textinfo="label+percent",
        )
    )
    fig.update_layout(
        title="Application status distribution",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1),
    )
    return fig


def activity_heatmap_chart(day_labels: list, data: list):
    """data: list of 7-element lists (one per week row)."""
    fig = go.Figure(
        go.Heatmap(
            z=data,
            x=day_labels,
            y=[f"Week {i+1}" for i in range(len(data))],
            colorscale=[[0, "#f0f4f8"], [0.5, "#7eb4e8"], [1, "#1e3a5f"]],
            text=data,
            texttemplate="%{text}",
            textfont={"size": 11},
        )
    )
    fig.update_layout(
        title="Application activity by day of week",
        margin=dict(l=60, r=20, t=40, b=40),
        height=220,
        xaxis_title="Day",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    )
    return fig
