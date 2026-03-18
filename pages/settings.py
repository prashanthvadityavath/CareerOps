"""Settings: Dark mode note, placeholder settings."""
import streamlit as st

def render_settings():
    st.subheader("Settings")
    st.markdown(
        "**Dark mode** — Use the menu in the top-right corner (⋮) → **Settings** → **Theme** to switch to dark mode."
    )
    st.divider()
    st.markdown("**Account** (placeholder)")
    st.text_input("Email", value="john.doe@example.com", disabled=True, key="settings_email")
    st.text_input("Display name", value="John Doe", key="settings_name")
    st.button("Save", key="settings_save", disabled=True)
