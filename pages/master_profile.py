"""Master Profile: Skills (tags), Projects, Work Experience; category toggles."""
import streamlit as st
from data.mock_data import MASTER_SKILLS, MASTER_SKILL_CATEGORIES, MASTER_PROJECTS, MASTER_EXPERIENCE

if "master_skills" not in st.session_state:
    st.session_state.master_skills = list(MASTER_SKILLS)

def render_master_profile():
    st.subheader("Master Profile")

    # Category toggles (filter display – mock)
    st.markdown("**Categories**")
    c1, c2, c3, c4 = st.columns(4)
    for i, cat in enumerate(MASTER_SKILL_CATEGORIES):
        with [c1, c2, c3, c4][i]:
            st.checkbox(cat, value=True, key=f"cat_{cat}")

    # Skills (tag-based)
    with st.expander("Skills", expanded=True):
        skill_input = st.text_input("Add skill", key="new_skill")
        if st.button("Add", key="add_skill") and skill_input.strip():
            st.session_state.master_skills.append(skill_input.strip())
            st.rerun()
        st.markdown(" ".join(f"`{s}`" for s in st.session_state.master_skills))

    # Projects
    with st.expander("Projects", expanded=True):
        for p in MASTER_PROJECTS:
            st.markdown(f"**{p['title']}** — *{p['category']}*")
            st.caption(p["description"])
            st.button("Edit", key=f"edit_proj_{p['title']}", disabled=True)
            st.markdown("---")

    # Work Experience
    with st.expander("Work Experience", expanded=True):
        for e in MASTER_EXPERIENCE:
            st.markdown(f"**{e['role']}** at {e['company']} ({e['start']} – {e['end']})")
            st.button("Edit", key=f"edit_exp_{e['role']}_{e['company']}", disabled=True)
            st.markdown("---")
