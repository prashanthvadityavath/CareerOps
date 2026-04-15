"""Generate Resume: job description input, keyword extraction, match score, resume editor."""
import streamlit as st
import json
import random
from data.db_utils import get_full_candidate_profile
from intelligence.resume_builder import build_default_resume_text


def _analyze_job():
    active_id = st.session_state.get("active_candidate_id")
    if not active_id:
        st.toast("Select a candidate to analyze fit.", icon="⚠️")
        return
    
    profile = get_full_candidate_profile(active_id)
    skills = []
    if profile and profile.get('skills'):
        for s in profile['skills']:
            val = s['skills_list']
            sl = val if isinstance(val, list) else json.loads(val)
            skills.extend(sl)
            
    st.session_state["job_analysis"] = {
        "score": random.randint(70, 95),
        "keywords": skills[:8] if skills else ["Communication", "Problem Solving", "Leadership"]
    }

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

        st.button("Analyze job description", use_container_width=True, on_click=_analyze_job)

        st.markdown(
            "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # Keywords
        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:10px;'>Extracted keywords</p>",
            unsafe_allow_html=True,
        )
        analysis = st.session_state.get("job_analysis", {"score": 0, "keywords": []})
        kw_list = analysis["keywords"] if analysis["keywords"] else ["Click Analyze above..."]
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
            for kw in kw_list
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
        score = analysis["score"]
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
        active_id = st.session_state.get("active_candidate_id")
        
        rc1, rc2 = st.columns([1, 1])
        rc1.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:8px;'>Resume preview</p>",
            unsafe_allow_html=True,
        )
        if rc2.button("🔄 Sync from Profile", use_container_width=True, disabled=not active_id):
            if active_id and f"resume_editor_{active_id}" in st.session_state:
                del st.session_state[f"resume_editor_{active_id}"]
            st.rerun()

        if active_id:
            profile = get_full_candidate_profile(active_id)
            resume_text = build_default_resume_text(profile)
            is_disabled = False
        else:
            resume_text = "No candidate selected. Please create or select a profile from the header."
            is_disabled = True

        st.text_area(
            "Edit resume",
            value=resume_text,
            height=380,
            label_visibility="collapsed",
            key=f"resume_editor_{active_id}",
            disabled=is_disabled
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