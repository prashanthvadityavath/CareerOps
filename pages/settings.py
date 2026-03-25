"""Settings: Dark mode note, placeholder settings, and DB diagnostics."""
import streamlit as st
from data.db_utils import run_query

def render_settings():
    st.subheader("Settings")
    st.markdown(
        "**Dark mode** — Use the menu in the top-right corner (⋮) → **Settings** → **Theme** to switch to dark mode."
    )
    st.divider()
    
    st.subheader("Account (placeholder)")
    st.text_input("Email", value="john.doe@example.com", disabled=True, key="settings_email")
    st.text_input("Display name", value="John Doe", key="settings_name")
    st.button("Save", key="settings_save", disabled=True)
    
    st.divider()
    
    # --- Database Diagnostic Section ---
    st.subheader("System Diagnostics")
    if st.button("Test Database Connection", type="primary"):
        with st.spinner("Connecting to PostgreSQL..."):
            # A simple query to check the connection and return the DB name and user
            test_query = "SELECT current_database(), current_user, version();"
            result = run_query(test_query)
            
            if result:
                st.success("Database connection successful!")
                st.json(result[0])
                
                # Additional check: Check if the tables exist
                table_check = run_query("SELECT count(*) FROM candidate;")
                st.info(f"Candidate table found. Current record count: {table_check[0]['count']}")
            else:
                st.error("Failed to connect. Check your secrets.toml credentials and ensure your local PostgreSQL server is running.")