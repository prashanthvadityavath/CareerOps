"""Generate Resume: job description input, keyword extraction, match score, resume editor."""
import json
import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from data.db_utils import get_full_candidate_profile, create_application, log_activity
from intelligence.resume_builder import build_default_resume_text
from intelligence.llm_matcher import analyze_job_match, MODEL_DEFAULTS


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
    model_name = st.session_state.get("model_name_input", "")
    profile = get_full_candidate_profile(active_id)
    profile_text = build_default_resume_text(profile)

    try:
        with st.spinner(f"Analyzing job match using {model_provider}..."):
            analysis = analyze_job_match(profile_text, job_desc, model_provider=model_provider, model_name=model_name)
            st.session_state["job_analysis"] = analysis
            st.toast(f"AI Analysis complete using {model_provider}!", icon="✅")
    except Exception as e:
        st.toast(f"AI Analysis failed: {str(e)[:100]}", icon="❌")

def _fetch_job_from_url():
    url = st.session_state.get("job_url_input", "").strip()
    if not url:
        st.toast("Please enter a Job URL first.", icon="⚠️")
        return
        
    try:
        with st.spinner("Fetching job description from URL..."):
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

def _log_application():
    active_id = st.session_state.get("active_candidate_id")
    company = st.session_state.get("gen_company", "").strip()
    role = st.session_state.get("gen_role", "").strip()
    
    analysis = st.session_state.get("job_analysis", {})
    score = analysis.get("score", 0)
    
    if active_id and company and role:
        create_application(active_id, company, role, f"{role} v1", score, "saved")
        log_activity(active_id, "application_submitted", f"Saved application for {role} at {company}")
        st.toast(f"Application for {company} logged to Kanban!", icon="✅")
        st.session_state["gen_company"] = ""
        st.session_state["gen_role"] = ""

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

        model_provider = st.selectbox(
            "Select AI Model",
            options=["Gemini", "Grok", "Qwen", "OpenAI", "Ollama"],
            key="model_provider_select",
            help="Choose the AI model for analysis.",
        )

        default_model_name = MODEL_DEFAULTS.get(model_provider, "")
        st.text_input(
            "Model Name (optional)",
            placeholder=f"Default: {default_model_name}",
            key="model_name_input",
            help=f"Optionally specify a model name. If left blank, '{default_model_name}' will be used."
        )

        # ── API Key Management ──
        if model_provider == "Ollama":
            key_name = "OLLAMA_BASE_URL"
            input_label = "Ollama Base URL"
            input_placeholder = "e.g., http://localhost:11434"
            expander_label = "Ollama Configuration"
            input_type = "default"
        else:
            key_name = f"{model_provider}_API_KEY".upper()
            input_label = f"{model_provider} API Key"
            input_placeholder = f"Enter your {model_provider} API Key here..."
            expander_label = f"{model_provider} API Key Configuration"
            input_type = "password"
        
        def get_saved_key():
            try:
                # For Ollama, provide a default if no key is saved
                if model_provider == "Ollama" and not os.path.exists("user_keys.json"):
                    return "http://localhost:11434"

                if os.path.exists("user_keys.json"):
                    with open("user_keys.json", "r") as f:
                        return json.load(f).get(key_name, "")
            except Exception:
                pass
            return ""

        def save_key(val):
            keys = {}
            if os.path.exists("user_keys.json"):
                try:
                    with open("user_keys.json", "r") as f:
                        keys = json.load(f)
                except Exception:
                    pass
            if val:
                keys[key_name] = val
            else:
                keys.pop(key_name, None)
            with open("user_keys.json", "w") as f:
                json.dump(keys, f)

        current_key = get_saved_key()
        
        def handle_save_key():
            val = st.session_state.get(f"input_{key_name}")
            if val:
                save_key(val)
                st.session_state[key_name] = val
                st.toast(f"{model_provider} API Key saved!", icon="✅")
            else:
                st.toast("Please enter a valid API key to save.", icon="⚠️")

        def handle_clear_key():
            save_key("")
            if key_name in st.session_state:
                del st.session_state[key_name]
            st.session_state[f"input_{key_name}"] = ""
            st.toast(f"{model_provider} API Key cleared!", icon="✅")

        with st.expander(expander_label, expanded=not bool(current_key)):
            st.text_input(
                input_label,
                value=current_key,
                type=input_type,
                placeholder=input_placeholder,
                key=f"input_{key_name}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("Save Key", key=f"save_{key_name}", on_click=handle_save_key)
            
            with col2:
                st.button("Clear Key", key=f"clear_{key_name}", on_click=handle_clear_key)

        st.button("Analyze job description", type="primary", on_click=_analyze_job)

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

        st.markdown("<div style='height:1px; background:rgba(128,128,128,0.12); margin:1rem 0;'></div>", unsafe_allow_html=True)
        c_comp, c_role = st.columns(2)
        company_input = c_comp.text_input("Company name", key="gen_company")
        role_input = c_role.text_input("Role title", key="gen_role")
        
        c1, c2 = st.columns(2)
        with c1:
            st.button("Download PDF", disabled=True)
        with c2:
            can_log = bool(active_id and company_input.strip() and role_input.strip())
            st.button("Save and log application", disabled=not can_log, on_click=_log_application)

        st.markdown(
            "<p style='font-size:11px; opacity:0.35; margin-top:6px;'>PDF export coming in Phase 3</p>",
            unsafe_allow_html=True,
        )