"""Generate Resume: job description input, keyword extraction, match score, resume editor."""
import streamlit as st
from data.mock_data import EXTRACTED_KEYWORDS, DEFAULT_RESUME_PREVIEW


def render_generate_resume() -> None:

    # ── Page header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 1.25rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Generate Resume
            </p>
            <p style="font-size:13px; opacity:0.5; margin:4px 0 0;">
                Tailor your resume to a specific job description
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")

    # ── Left: input + analysis ───────────────────────────────────
    with left:
        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:6px;'>Job URL</p>",
            unsafe_allow_html=True,
        )
        st.text_input(
            "Job URL",
            placeholder="https://...",
            label_visibility="collapsed",
            key="job_url_input",
        )

        st.markdown(
            "<p style='font-size:12px; opacity:0.4; text-align:center; margin:6px 0;'>or paste job description below</p>",
            unsafe_allow_html=True,
        )

        st.text_area(
            "Job description",
            height=130,
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
            key="job_desc_input",
        )

        st.button("Analyze job description", use_container_width=True)

        st.markdown(
            "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # Keywords
        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:10px;'>Extracted keywords</p>",
            unsafe_allow_html=True,
        )
        keyword_pills = "".join([
            f"""<span style="
                display:inline-block;
                font-size:11px;
                padding:3px 10px;
                border-radius:12px;
                border:1px solid rgba(128,128,128,0.2);
                margin:0 4px 6px 0;
                opacity:0.75;
            ">{kw}</span>"""
            for kw in EXTRACTED_KEYWORDS
        ])
        st.markdown(
            f"<div style='line-height:2;'>{keyword_pills}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # Match score
        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:8px;'>Match score</p>",
            unsafe_allow_html=True,
        )
        score = 87
        score_color = "#1D9E75" if score >= 80 else "#BA7517" if score >= 60 else "rgba(128,128,128,0.6)"
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:12px;
            ">
                <div style="
                    flex:1;
                    height:6px;
                    background:rgba(128,128,128,0.12);
                    border-radius:3px;
                    overflow:hidden;
                ">
                    <div style="
                        width:{score}%;
                        height:100%;
                        background:{score_color};
                        border-radius:3px;
                        transition:width 0.4s ease;
                    "></div>
                </div>
                <span style="font-size:13px; font-weight:600; color:{score_color}; min-width:36px;">
                    {score}%
                </span>
            </div>
            <p style="font-size:11px; opacity:0.4; margin:6px 0 0;">
                Mock score — connect backend to calculate live
            </p>
            """,
            unsafe_allow_html=True,
        )

    # ── Right: resume editor ─────────────────────────────────────
    with right:
        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:8px;'>Resume preview</p>",
            unsafe_allow_html=True,
        )
        st.text_area(
            "Edit resume",
            value=DEFAULT_RESUME_PREVIEW,
            height=380,
            label_visibility="collapsed",
            key="resume_preview",
        )

        c1, c2 = st.columns(2)
        with c1:
            st.button("Download PDF", use_container_width=True, disabled=True)
        with c2:
            st.button("Save and log application", use_container_width=True, disabled=True)

        st.markdown(
            "<p style='font-size:11px; opacity:0.35; margin-top:6px;'>PDF export and save coming in Phase 3</p>",
            unsafe_allow_html=True,
        )