"""Top header bar: logo, daily goal progress, notifications, user avatar."""
import streamlit as st
from pathlib import Path
from config import DAILY_APPLICATIONS_DONE_KEY, DAILY_GOAL_KEY, CURRENT_PAGE_KEY
from data.db_utils import run_query


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

    /* ── Nav buttons: Minimalist menu style ─── */
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) {
        background: transparent;
        padding: 0;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        justify-content: center;
    }
    /* Force columns to shrink-wrap their text instead of stretching */
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) > div {
        width: auto !important;
        flex: 0 1 auto !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) [data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 12px 4px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: inherit !important;
        opacity: 0.6;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: none !important;
        transform: none !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) [data-testid="stButton"] button:hover {
        opacity: 0.9 !important;
        color: #185FA5 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) [data-testid="stButton"] button p strong {
        color: #185FA5 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) [data-testid="stButton"] button:has(p strong) {
        opacity: 1 !important;
        border-bottom: 2px solid #185FA5 !important;
    }

    /* ── Page content padding ────────────────────────────────── */
    .co-page {
        padding: 0 1.5rem;
    }

    /* ── Profile Selectbox refinements ───────────────────────── */
    /* Hide the blinking text cursor so it feels like a standard dropdown */
    div[data-testid="stSelectbox"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
    }
    /* Tighter dimensions to fit nicely in the header */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 34px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    """

    st.markdown(
        f"<style>{file_css}\n{header_css}</style>",
        unsafe_allow_html=True,
    )


def render_header(daily_done: int = 0, daily_goal: int = 5) -> None:
    """
    Render the sticky top header bar.
    """

    # 1. Fetch Candidates from Database
    candidates = run_query("SELECT id, full_name, daily_goal FROM candidate ORDER BY id")
    
    cand_options = {}
    cand_goals = {}
    if candidates:
        for c in candidates:
            name = c['full_name'] or f"Profile {c['id']}"
            cand_options[name] = c['id']
            cand_goals[c['id']] = c.get('daily_goal') or 5

    cand_options["Create new candidate"] = None

    st.session_state["_cand_options_map"] = cand_options

    def _update_active_profile():
        selected = st.session_state.get("header_profile")
        mapping = st.session_state.get("_cand_options_map", {})
        if selected in mapping:
            cid = mapping[selected]
            st.session_state["active_candidate_id"] = cid
            st.session_state["active_candidate_name"] = selected
            if cid is not None:
                st.query_params["candidate_id"] = str(cid)
            else:
                if "candidate_id" in st.query_params:
                    del st.query_params["candidate_id"]
                st.session_state[CURRENT_PAGE_KEY] = "Master Profile"
                st.query_params["page"] = "Master Profile"

    # Check query params for initial load persistence (like a hard refresh)
    if "candidate_id" in st.query_params and "active_candidate_id" not in st.session_state:
        try:
            param_id = int(st.query_params["candidate_id"])
            if any(c["id"] == param_id for c in candidates):
                st.session_state["active_candidate_id"] = param_id
        except ValueError:
            pass

    # 2. Determine active selection
    current_id = st.session_state.get("active_candidate_id")
    
    if "active_candidate_id" not in st.session_state:
        if candidates:
            current_id = candidates[0]['id']
            st.session_state["active_candidate_id"] = current_id
            st.query_params["candidate_id"] = str(current_id)
        else:
            st.session_state["active_candidate_id"] = None
            current_id = None

    current_name = next((name for name, cid in cand_options.items() if cid == current_id), "Create new candidate")
    
    # Force sync widget state
    if st.session_state.get("header_profile") != current_name:
        st.session_state["header_profile"] = current_name

    # 3. Update goal based on active candidate
    current_id = st.session_state.get("active_candidate_id")
    active_goal = cand_goals.get(current_id, daily_goal)
    st.session_state[DAILY_GOAL_KEY] = active_goal

    pct = min(int((daily_done / active_goal) * 100), 100) if active_goal > 0 else 0
    goal_color = "#1D9E75" if pct >= 100 else "#185FA5" if pct >= 50 else "#BA7517"

    st.markdown(
        f"""
        <div class="co-header">
            <div class="co-logo">
                <div class="co-logo-icon">C</div>
                CareerOps
            </div>
            <div class="co-goal-pill">
                <span>{daily_done}/{active_goal} today</span>
                <div class="co-goal-bar-track">
                    <div class="co-goal-bar-fill" style="width:{pct}%; background:{goal_color};"></div>
                </div>
                <span style="opacity:0.6; font-size:11px;">{pct}%</span>
            </div>
            <div class="co-right" style="gap: 20px;">
                <div class="co-icon-btn" title="Notifications">🔔</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # 3. Render the Dropdown aligned to the right via columns
    # We use columns to place the selectbox over the right side area
    _, right_col = st.columns([5, 1])
    with right_col:
        # Add negative margin to pull it up into the header space visually
        st.markdown("<div style='margin-top: -45px;'></div>", unsafe_allow_html=True)
        st.selectbox(
            "Active Profile",
            options=list(cand_options.keys()),
            label_visibility="collapsed",
            key="header_profile",
            on_change=_update_active_profile
        )