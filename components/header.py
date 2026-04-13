"""Top header bar: logo, daily goal progress, notifications, user avatar."""
import streamlit as st
from pathlib import Path
from config import DAILY_APPLICATIONS_DONE_KEY, DAILY_GOAL_KEY, CURRENT_PAGE_KEY


def inject_css() -> None:
    """Inject global CSS: .streamlit/style.css + header component styles."""
    project_root = Path(__file__).resolve().parent.parent
    css_path = project_root / ".streamlit" / "style.css"

    # Base file CSS
    file_css = ""
    if css_path.is_file():
        file_css = css_path.read_text(encoding="utf-8")

    # Header-specific styles injected here so header.py is self-contained
    header_css = """
    /* ── Global resets ───────────────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0 !important; }
    [data-testid="stSidebar"] { display: none; }

    /* ── Top header bar ──────────────────────────────────────── */
    .co-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1.5rem;
        height: 56px;
        background: var(--background-color);
        border-bottom: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 0;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    /* Logo */
    .co-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: inherit;
        text-decoration: none;
    }
    .co-logo-icon {
        width: 28px;
        height: 28px;
        background: #185FA5;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #E6F1FB;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
    }

    /* Daily goal pill */
    .co-goal-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(128,128,128,0.07);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        color: inherit;
        opacity: 0.85;
    }
    .co-goal-bar-track {
        width: 60px;
        height: 4px;
        background: rgba(128,128,128,0.2);
        border-radius: 2px;
        overflow: hidden;
    }
    .co-goal-bar-fill {
        height: 100%;
        border-radius: 2px;
        background: #1D9E75;
        transition: width 0.3s ease;
    }

    /* Right controls */
    .co-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .co-icon-btn {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: transparent;
        border: 1px solid rgba(128,128,128,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.15s;
    }
    .co-icon-btn:hover { background: rgba(128,128,128,0.1); }

    /* Avatar */
    .co-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #185FA5;
        color: #E6F1FB;
        font-size: 11px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        flex-shrink: 0;
    }

    /* ── Navigation bar ──────────────────────────────────────── */
    .co-navbar {
        display: flex;
        align-items: flex-end;
        gap: 0;
        padding: 0 1.5rem;
        background: var(--background-color);
        border-bottom: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 1.5rem;
    }
    .co-nav-item {
        padding: 10px 16px;
        font-size: 13px;
        color: inherit;
        opacity: 0.55;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        white-space: nowrap;
        transition: opacity 0.15s;
        text-decoration: none;
    }
    .co-nav-item:hover { opacity: 0.85; }
    .co-nav-item.co-nav-active {
        opacity: 1;
        color: #185FA5;
        border-bottom: 2px solid #185FA5;
        font-weight: 500;
    }

    /* ── Nav buttons: strip Streamlit default button styling ─── */
    div[data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        padding: 10px 16px !important;
        font-size: 13px !important;
        color: inherit !important;
        opacity: 0.55;
        transition: opacity 0.15s, border-color 0.15s;
        width: 100%;
    }
    div[data-testid="stHorizontalBlock"] [data-testid="stButton"] button:hover {
        opacity: 0.85 !important;
        color: inherit !important;
    }
    div[data-testid="stHorizontalBlock"] [data-testid="stButton"] button p strong {
        color: #185FA5 !important;
        font-weight: 500;
    }
    div[data-testid="stHorizontalBlock"] [data-testid="stButton"] button:has(p strong) {
        opacity: 1 !important;
        border-bottom: 2px solid #185FA5 !important;
    }

    /* ── Page content padding ────────────────────────────────── */
    .co-page {
        padding: 0 1.5rem;
    }
    """

    st.markdown(
        f"<style>{file_css}\n{header_css}</style>",
        unsafe_allow_html=True,
    )


def render_header(daily_done: int = 0, daily_goal: int = 5) -> None:
    """
    Render the sticky top header bar.

    Args:
        daily_done: Number of applications submitted today.
        daily_goal: Daily application target.
    """
    pct = min(int((daily_done / daily_goal) * 100), 100) if daily_goal > 0 else 0
    goal_color = "#1D9E75" if pct >= 100 else "#185FA5" if pct >= 50 else "#BA7517"

    # Get candidate name from session state if available, fallback to placeholder
    candidate_name = st.session_state.get("active_candidate_name", "You")
    initials = "".join(w[0].upper() for w in candidate_name.split()[:2]) if candidate_name != "You" else "JD"

    st.markdown(
        f"""
        <div class="co-header">
            <div class="co-logo">
                <div class="co-logo-icon">C</div>
                CareerOps
            </div>
            <div class="co-goal-pill">
                <span>{daily_done}/{daily_goal} today</span>
                <div class="co-goal-bar-track">
                    <div class="co-goal-bar-fill" style="width:{pct}%; background:{goal_color};"></div>
                </div>
                <span style="opacity:0.6; font-size:11px;">{pct}%</span>
            </div>
            <div class="co-right">
                <div class="co-icon-btn" title="Notifications">🔔</div>
                <div class="co-avatar" title="{candidate_name}">{initials}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )