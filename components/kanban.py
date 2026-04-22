"""Kanban card and column helpers."""
import streamlit as st
from data.db_utils import move_application, log_activity

KANBAN_COLUMNS = [
    ("saved",          "Saved"),
    ("applied",        "Applied"),
    ("interviewing",   "Interviewing"),
    ("offer_rejected", "Offer / Rejected"),
]

MOVE_OPTIONS = [
    ("saved",          "Saved"),
    ("applied",        "Applied"),
    ("interviewing",   "Interviewing"),
    ("offered",        "Offered"),
    ("rejected",       "Rejected"),
]

# Status accent colors — left border on each card
_COLUMN_ACCENT = {
    "saved":          "rgba(128,128,128,0.4)",
    "applied":        "#185FA5",
    "interviewing":   "#BA7517",
    "offer_rejected": "rgba(128,128,128,0.4)",
    "offered":        "#1D9E75",
    "rejected":       "#D85A30",
}

# Match score color thresholds
def _score_color(score: int) -> str:
    if score >= 80:
        return "#1D9E75"
    if score >= 60:
        return "#BA7517"
    return "rgba(128,128,128,0.7)"


def _on_move_callback(app_id: str, key_suffix: str) -> None:
    key = f"move_{app_id}_{key_suffix}"
    label = st.session_state.get(key)
    if not label:
        return
    target_id = next(
        (cid for cid, lbl in MOVE_OPTIONS if lbl == label), None
    )
    if target_id is not None:
        move_application(int(app_id), target_id)
        
        active_id = st.session_state.get("active_candidate_id")
        if active_id:
            log_activity(active_id, "status_changed", f"Application moved to {label}")


def render_kanban_card(
    app_id: str,
    company: str,
    role: str,
    resume_tag: str,
    match_score: int,
    date_applied: str,
    current_column: str,
    key_suffix: str = "",
) -> None:
    """
    Render one application card with a move selector.
    Left border accent reflects current pipeline stage.
    """
    accent = _COLUMN_ACCENT.get(current_column, "rgba(128,128,128,0.3)")
    score_color = _score_color(match_score)

    bg_style = ""
    if current_column == "offered":
        bg_style = "background-color: rgba(29, 158, 117, 0.15);"
    elif current_column == "rejected":
        bg_style = "background-color: rgba(216, 90, 48, 0.15);"

    st.markdown(
        f"""
        <div class="kanban-card" style="border-left: 3px solid {accent}; {bg_style}">
            <p style="font-size:13px; font-weight:600; margin:0 0 2px;">{company}</p>
            <p style="font-size:12px; opacity:0.65; margin:0 0 6px;">{role}</p>
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="
                    font-size:11px;
                    padding:2px 8px;
                    border-radius:10px;
                    border:1px solid rgba(128,128,128,0.2);
                    opacity:0.7;
                ">{resume_tag}</span>
                <span style="font-size:12px; font-weight:600; color:{score_color};">
                    {match_score}%
                </span>
            </div>
            <p style="font-size:11px; opacity:0.45; margin:6px 0 0;">{date_applied}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    other_columns = [lbl for cid, lbl in MOVE_OPTIONS if cid != current_column]
    if other_columns:
        st.selectbox(
            "Move to",
            options=other_columns,
            index=None,
            placeholder="Move to...",
            key=f"move_{app_id}_{key_suffix}",
            label_visibility="collapsed",
            on_change=_on_move_callback,
            args=(app_id, key_suffix),
        )