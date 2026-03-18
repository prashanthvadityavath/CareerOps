"""Activity timeline components."""
import streamlit as st

EVENT_ICONS = {
    "resume_generated": "📄",
    "application_submitted": "📤",
    "interview_update": "📅",
    "status_changed": "🔄",
}


def render_timeline_item(event_type: str, label: str, timestamp: str, key_suffix: str = ""):
    icon = EVENT_ICONS.get(event_type, "•")
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: flex-start;
            margin-bottom: 14px;
            padding-left: 8px;
            border-left: 2px solid #e8eaed;
            margin-left: 8px;
        ">
            <span style="font-size: 1rem; margin-right: 10px;">{icon}</span>
            <div>
                <div style="font-size: 0.9rem; color: #1a1a2e;">{label}</div>
                <div style="font-size: 0.75rem; color: #5f6368;">{timestamp}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_activity_timeline(events: list, key_suffix: str = ""):
    """Render full vertical timeline from list of dicts with type, label, timestamp."""
    for i, ev in enumerate(events):
        render_timeline_item(
            ev.get("type", ""),
            ev.get("label", ""),
            ev.get("timestamp", ""),
            key_suffix=f"{key_suffix}_{i}",
        )
