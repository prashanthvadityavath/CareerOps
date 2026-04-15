"""Settings: account preferences, daily goal, and database diagnostics."""
import streamlit as st
from config import DAILY_GOAL_KEY, DAILY_APPLICATIONS_DONE_KEY, DEFAULT_DAILY_GOAL
from data.db_utils import run_query


def _divider() -> None:
    st.markdown(
        "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>",
        unsafe_allow_html=True,
    )


def _section_header(title: str, subtitle: str = "") -> None:
    sub = (
        f"<p style='font-size:13px; opacity:0.5; margin:2px 0 12px;'>{subtitle}</p>"
        if subtitle else ""
    )
    st.markdown(
        f"<p style='font-size:15px; font-weight:600; margin:0 0 4px;'>{title}</p>{sub}",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render_settings() -> None:

    # ── Page header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 1.25rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Settings
            </p>
            <p style="font-size:13px; opacity:0.5; margin:4px 0 0;">
                Preferences and system diagnostics
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Account ──────────────────────────────────────────────────
    _section_header("Account", "Placeholder — authentication coming in Phase 4.")
    c1, c2 = st.columns(2)
    c1.text_input("Email", value="john.doe@example.com", disabled=True, key="settings_email")
    c2.text_input("Display name", value="John Doe", disabled=True, key="settings_name")
    st.button("Save account", disabled=True, key="settings_save")

    _divider()

    # ── Daily goal ───────────────────────────────────────────────
    _section_header("Daily application goal", "Sets the target shown in the header progress bar.")

    active_id = st.session_state.get("active_candidate_id")
    current_goal = st.session_state.get(DAILY_GOAL_KEY, DEFAULT_DAILY_GOAL)
    
    if active_id:
        res = run_query("SELECT daily_goal FROM candidate WHERE id = %s", (active_id,))
        if res and res[0].get("daily_goal"):
            current_goal = res[0]["daily_goal"]

    new_goal = st.number_input(
        "Target applications per day",
        min_value=1,
        max_value=50,
        step=1,
        value=current_goal,
        key="settings_daily_goal",
    )
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("Save goal", use_container_width=True, disabled=not active_id):
            run_query("UPDATE candidate SET daily_goal = %s WHERE id = %s", (new_goal, active_id), fetch_results=False)
            st.session_state[DAILY_GOAL_KEY] = new_goal
            st.toast(f"Goal saved: {new_goal}!", icon="✅")

    _divider()

    # ── Appearance ───────────────────────────────────────────────
    _section_header("Appearance", "Theme is controlled by Streamlit itself.")
    st.markdown(
        "<p style='font-size:13px; opacity:0.6;'>"
        "To switch between light and dark mode, open the Streamlit menu "
        "(top-right corner) and go to Settings → Theme."
        "</p>",
        unsafe_allow_html=True,
    )

    _divider()

    # ── Database diagnostics ─────────────────────────────────────
    _section_header("Database diagnostics", "Verify your PostgreSQL connection and schema.")

    if st.button("Test database connection", key="db_test_btn"):
        with st.spinner("Connecting to PostgreSQL..."):
            result = run_query("SELECT current_database(), current_user, version();")

            if result:
                st.success("Connection successful.")
                row = result[0]
                st.markdown(
                    f"""
                    <div style="
                        border:1px solid rgba(128,128,128,0.15);
                        border-radius:8px;
                        padding:12px 16px;
                        font-size:13px;
                        margin-top:8px;
                    ">
                        <p style="margin:0 0 4px;">
                            <span style="opacity:0.5;">Database</span>
                            &nbsp;&nbsp;{row.get('current_database', '—')}
                        </p>
                        <p style="margin:0 0 4px;">
                            <span style="opacity:0.5;">User</span>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            {row.get('current_user', '—')}
                        </p>
                        <p style="margin:0; opacity:0.45; font-size:11px;">
                            {row.get('version', '')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                table_check = run_query("SELECT count(*) FROM candidate;")
                if table_check:
                    count = table_check[0]["count"]
                    st.markdown(
                        f"<p style='font-size:13px; opacity:0.6; margin-top:10px;'>"
                        f"Candidate table found — {count} record{'s' if count != 1 else ''}.</p>",
                        unsafe_allow_html=True,
                    )
            else:
                st.error(
                    "Connection failed. Check your .streamlit/secrets.toml "
                    "credentials and ensure PostgreSQL is running."
                )