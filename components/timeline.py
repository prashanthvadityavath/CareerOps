"""Activity timeline component."""
import streamlit as st

# Maps event type to a small colored dot style instead of emoji
_EVENT_COLOR = {
    "resume_generated":      "#185FA5",
    "application_submitted": "#1D9E75",
    "interview_update":      "#BA7517",
    "status_changed":        "rgba(128,128,128,0.6)",
}


def render_timeline_item(
    event_type: str,
    label: str,
    timestamp: str,
    key_suffix: str = "",
) -> None:
    color = _EVENT_COLOR.get(event_type, "rgba(128,128,128,0.4)")
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 14px;
            padding-left: 4px;
        ">
            <div style="
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: {color};
                margin-top: 5px;
                flex-shrink: 0;
            "></div>
            <div>
                <p style="font-size:13px; margin:0 0 2px; line-height:1.4;">{label}</p>
                <p style="font-size:11px; opacity:0.45; margin:0;">{timestamp}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_activity_timeline(events: list, key_suffix: str = "") -> None:
    """Render a vertical timeline from a list of event dicts."""
    if not events:
        st.markdown(
            "<p style='font-size:13px; opacity:0.45;'>No recent activity.</p>",
            unsafe_allow_html=True,
        )
        return
    for i, ev in enumerate(events):
        render_timeline_item(
            ev.get("type", ""),
            ev.get("label", ""),
            ev.get("timestamp", ""),
            key_suffix=f"{key_suffix}_{i}",
        )