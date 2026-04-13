"""Chart helpers – Plotly figures, dark/light mode safe."""
import pandas as pd
import plotly.graph_objects as go

# ── Shared design tokens ─────────────────────────────────────────────────────
_BLUE       = "#185FA5"
_BLUE_LIGHT = "rgba(24, 95, 165, 0.12)"
_GREEN      = "#1D9E75"
_AMBER      = "#BA7517"
_GRAY       = "rgba(128,128,128,0.5)"

# Categorical palette for pie / multi-series
_PALETTE = ["#185FA5", "#1D9E75", "#BA7517", "#7F77DD", "#D85A30"]

_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="rgba(128,128,128,0.9)"),
    margin=dict(l=40, r=20, t=44, b=40),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(128,128,128,0.15)",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(128,128,128,0.1)",
        zeroline=False,
        tickfont=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="rgba(0,0,0,0.75)",
        font_color="white",
        font_size=12,
        bordercolor="rgba(0,0,0,0)",
    ),
)

_MODEBAR = {"displayModeBar": False}


def _apply_base(fig: go.Figure, title: str, height: int = 280) -> go.Figure:
    """Apply shared layout to any figure."""
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(
            text=title,
            font=dict(size=14, weight="normal"),
            x=0,
            xanchor="left",
            pad=dict(b=8),
        ),
        height=height,
    )
    return fig


# ── Individual charts ────────────────────────────────────────────────────────

def applications_per_week_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=df["week"],
            y=df["applications"],
            mode="lines+markers",
            line=dict(color=_BLUE, width=2),
            marker=dict(size=6, color=_BLUE),
            fill="tozeroy",
            fillcolor=_BLUE_LIGHT,
            hovertemplate="%{x}<br><b>%{y} applications</b><extra></extra>",
        )
    )
    _apply_base(fig, "Applications per week")
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Applications",
    )
    return fig


def resume_version_interview_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=df["version"],
            y=df["interview_rate"],
            marker=dict(
                color=df["interview_rate"],
                colorscale=[
                    [0.0, "rgba(24,95,165,0.3)"],
                    [1.0, _BLUE],
                ],
                showscale=False,
            ),
            text=df["interview_rate"],
            texttemplate="%{text}%",
            textposition="outside",
            textfont=dict(size=11),
            hovertemplate="%{x}<br><b>%{y}% interview rate</b><extra></extra>",
        )
    )
    _apply_base(fig, "Resume version vs interview rate")
    fig.update_layout(
        xaxis_title="Resume version",
        yaxis_title="Interview rate (%)",
        xaxis_tickangle=-30,
        showlegend=False,
        margin=dict(l=40, r=20, t=44, b=80),
    )
    return fig


def status_distribution_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=df["status"],
            values=df["count"],
            hole=0.52,
            marker=dict(
                colors=_PALETTE,
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            textinfo="label+percent",
            textfont=dict(size=11),
            hovertemplate="%{label}<br><b>%{value} applications</b> (%{percent})<extra></extra>",
        )
    )
    _apply_base(fig, "Application status distribution", height=300)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=44, b=20),
    )
    return fig


def activity_heatmap_chart(day_labels: list, data: list) -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=data,
            x=day_labels,
            y=[f"Week {i + 1}" for i in range(len(data))],
            colorscale=[
                [0.0, "rgba(24,95,165,0.05)"],
                [0.5, "rgba(24,95,165,0.4)"],
                [1.0, _BLUE],
            ],
            text=data,
            texttemplate="%{text}",
            textfont=dict(size=11, color="rgba(255,255,255,0.9)"),
            showscale=False,
            hovertemplate="%{x}<br><b>%{z} applications</b><extra></extra>",
            xgap=3,
            ygap=3,
        )
    )
    _apply_base(fig, "Activity by day of week", height=220)
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11)),
        margin=dict(l=60, r=20, t=44, b=40),
    )
    return fig