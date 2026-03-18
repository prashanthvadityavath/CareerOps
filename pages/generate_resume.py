"""Generate Resume: Job URL/description input, analyze, keywords, match gauge, resume preview."""
import streamlit as st
from data.mock_data import EXTRACTED_KEYWORDS, DEFAULT_RESUME_PREVIEW

def render_generate_resume():
    st.subheader("Generate Resume")
    left, right = st.columns(2)

    with left:
        job_url = st.text_input("Job URL", placeholder="https://...")
        st.markdown("— or paste job description —")
        job_desc = st.text_area("Job description", height=120, placeholder="Paste the full job description here...")
        if st.button("Analyze Job Description"):
            st.success("Analysis complete (mock).")
        st.caption("Uses mock analysis until backend is connected.")
        st.markdown("**Extracted keywords**")
        keyword_str = " · ".join(EXTRACTED_KEYWORDS)
        st.markdown(f"*{keyword_str}*")
        st.markdown("**Match score**")
        st.progress(0.87)
        st.caption("87% match (mock)")

    with right:
        st.markdown("**Resume preview**")
        resume_text = st.text_area("Edit resume", value=DEFAULT_RESUME_PREVIEW, height=320, key="resume_preview")
        c1, c2 = st.columns(2)
        with c1:
            st.button("Download PDF", disabled=True)
        with c2:
            st.button("Save & Log Application", disabled=True)
        st.caption("PDF and Save are placeholders (no backend).")
