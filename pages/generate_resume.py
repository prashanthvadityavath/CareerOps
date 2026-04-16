"""Generate Resume: job description input, keyword extraction, match score, resume editor."""
import streamlit as st
import requests
from bs4 import BeautifulSoup
from data.db_utils import get_full_candidate_profile
from intelligence.resume_builder import build_default_resume_text
from intelligence.llm_matcher import analyze_job_match


def _analyze_job():
    active_id = st.session_state.get("active_candidate_id")
    if not active_id:
        st.toast("Select a candidate to analyze fit.", icon="⚠️")
        return
    
    job_desc = st.session_state.get("job_desc_input", "").strip()
    if not job_desc:
        st.toast("Please fetch or paste a job description first.", icon="⚠️")
        return
    
    model_provider = st.session_state.get("model_provider_select", "Gemini")
    profile = get_full_candidate_profile(active_id)
    profile_text = build_default_resume_text(profile)

    try:
        analysis = analyze_job_match(profile_text, job_desc, model_provider=model_provider)
        st.session_state["job_analysis"] = analysis
        st.toast(f"AI Analysis complete using {model_provider}!", icon="✅")
    except Exception as e:
        st.toast(f"AI Analysis failed: {str(e)[:50]}", icon="❌")

def _fetch_job_from_url():
    url = st.session_state.get("job_url_input", "").strip()
    if not url:
        st.toast("Please enter a Job URL first.", icon="⚠️")
        return
        
    try:
        # Basic headers to bypass simple bot protections
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove irrelevant elements like scripts, styles, navs
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.extract()
            
        # Extract text and clean up excess whitespace
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        
        st.session_state["job_desc_input"] = cleaned_text
        st.toast("Job description fetched!", icon="✅")
    except Exception as e:
        st.toast(f"Failed to fetch URL: {str(e)[:50]}", icon="❌")

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
    
        url_col, btn_col = st.columns([3, 1])
        with url_col:
            st.text_input(
                "Job URL",
                placeholder="https://...",
                label_visibility="collapsed",
                key="job_url_input",
            )
        with btn_col:
            st.button("Fetch", on_click=_fetch_job_from_url, use_container_width=True)

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

        st.selectbox(
            "Select AI Model",
            options=["Gemini", "Grok", "Qwen"],
            key="model_provider_select",
            help="Choose the AI model for analysis. Requires the corresponding API key in your secrets.",
        )

        st.button("Analyze job description", use_container_width=True, on_click=_analyze_job)

        st.markdown(
            "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # Keywords
        analysis = st.session_state.get("job_analysis", {})
        score = analysis.get("score", 0)
        matching = analysis.get("matching_keywords", [])
        missing = analysis.get("missing_keywords", [])
        checklist = analysis.get("checklist", {})
        rec = analysis.get("recommendation", "")

        st.markdown(
            "<p style='font-size:13px; font-weight:500; margin-bottom:10px;'>Keyword Analysis</p>",
            unsafe_allow_html=True,
        )
        
        if not matching and not missing:
            keyword_pills = "<p style='font-size:12px; opacity:0.6;'>Click Analyze above to extract keywords...</p>"
        else:
            match_pills = "".join([
                f"""<span style="display:inline-block; font-size:11px; padding:3px 10px; border-radius:12px; border:1px solid #1D9E75; background:rgba(29, 158, 117, 0.1); color:#1D9E75; margin:0 4px 6px 0;">✓ {kw}</span>"""
                for kw in matching
            ])
            miss_pills = "".join([
                f"""<span style="display:inline-block; font-size:11px; padding:3px 10px; border-radius:12px; border:1px solid rgba(128,128,128,0.3); color:rgba(128,128,128,0.8); margin:0 4px 6px 0;">✗ {kw}</span>"""
                for kw in missing
            ])
            keyword_pills = match_pills + miss_pills

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
            """,
            unsafe_allow_html=True,
        )
        
        if rec:
            st.markdown(f"<p style='font-size:12px; font-weight:500; margin:8px 0 0;'>💡 {rec}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:11px; opacity:0.4; margin:6px 0 0;'>Connect backend to calculate live</p>", unsafe_allow_html=True)

        # Checklist
        if checklist:
            st.markdown("<div style='height:1px; background:rgba(128,128,128,0.12); margin:1.25rem 0;'></div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:13px; font-weight:500; margin-bottom:10px;'>Quick Requirements</p>", unsafe_allow_html=True)
            
            def _bool_icon(val):
                if isinstance(val, bool):
                    return "✅ Yes" if val else "❌ No"
                return str(val)
            
            items_html = ""
            for key, val in checklist.items():
                label = key.replace('_', ' ').capitalize()
                items_html += f"<li style='font-size:12px; margin-bottom:4px;'><span style='opacity:0.7;'>{label}:</span> <strong>{_bool_icon(val)}</strong></li>"
            
            st.markdown(f"<ul style='margin:0; padding-left:18px;'>{items_html}</ul>", unsafe_allow_html=True)

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