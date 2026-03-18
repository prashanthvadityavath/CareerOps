"""Kanban card and column helpers. Move via dropdown + session state."""
import streamlit as st
from config import PENDING_MOVES_KEY

KANBAN_COLUMNS = [
    ("saved", "Saved"),
    ("applied", "Applied"),
    ("interviewing", "Interviewing"),
    ("offer_rejected", "Offer / Rejected"),
]


def _on_move_callback(app_id: str, key_suffix: str):
    """On 'Move to' dropdown change: append move to pending and rerun."""
    key = f"move_{app_id}_{key_suffix}"
    label = st.session_state.get(key)
    if not label:
        return
    target_id = next((cid for cid, lbl in KANBAN_COLUMNS if lbl == label), None)
    if target_id is not None:
        if PENDING_MOVES_KEY not in st.session_state:
            st.session_state[PENDING_MOVES_KEY] = []
        st.session_state[PENDING_MOVES_KEY].append((app_id, target_id))
    st.rerun()


def render_kanban_card(app_id: str, company: str, role: str, resume_tag: str, match_score: int, date_applied: str, current_column: str, key_suffix: str = ""):
    """
    Render one application card with a "Move to" dropdown.
    Changing the dropdown immediately moves the card (appends to PENDING_MOVES_KEY and reruns).
    Caller should process pending moves and update applications then clear PENDING_MOVES_KEY.
    """
    with st.container():
        st.markdown(
            f"""
            <div style="
                background: #fff;
                border: 1px solid #e8eaed;
                border-radius: 10px;
                padding: 12px 14px;
                margin-bottom: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            ">
                <div style="font-weight: 600; color: #1a1a2e;">{company}</div>
                <div style="font-size: 0.9rem; color: #5f6368;">{role}</div>
                <div style="font-size: 0.8rem; color: #1e3a5f; margin-top: 4px;">{resume_tag}</div>
                <div style="margin-top: 6px; font-size: 0.85rem;">
                    <span style="color: #5f6368;">Match:</span> <strong>{match_score}%</strong>
                    <span style="color: #5f6368; margin-left: 8px;">{date_applied}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        other_columns = [(cid, label) for cid, label in KANBAN_COLUMNS if cid != current_column]
        if other_columns:
            st.selectbox(
                "Move to",
                options=[label for _, label in other_columns],
                key=f"move_{app_id}_{key_suffix}",
                label_visibility="collapsed",
                on_change=_on_move_callback,
                args=(app_id, key_suffix),
            )
