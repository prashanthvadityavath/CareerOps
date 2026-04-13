"""Master Profile: multi-candidate management with full CRUD."""
import streamlit as st
import json
from data.db_utils import run_query


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _load_json_field(value) -> list:
    """Safely parse a JSONB field that may already be a list or a JSON string."""
    if not value:
        return []
    return value if isinstance(value, list) else json.loads(value)


def _section_header(title: str, count: int | None = None) -> None:
    badge = ""
    if count is not None:
        badge = f"""<span style="
            font-size:11px; font-weight:500;
            padding:1px 7px; border-radius:10px;
            border:1px solid rgba(128,128,128,0.2);
            opacity:0.55; margin-left:8px;
        ">{count}</span>"""
    st.markdown(
        f"<p style='font-size:13px; font-weight:500; margin:0 0 12px;'>{title}{badge}</p>",
        unsafe_allow_html=True,
    )


def _divider() -> None:
    st.markdown(
        "<div style='height:1px; background:rgba(128,128,128,0.12); margin:1rem 0;'></div>",
        unsafe_allow_html=True,
    )


def _empty_state(message: str) -> None:
    st.markdown(
        f"""
        <div style="
            border:1px dashed rgba(128,128,128,0.25);
            border-radius:8px; padding:16px;
            text-align:center; font-size:12px; opacity:0.45;
            margin-bottom:12px;
        ">{message}</div>
        """,
        unsafe_allow_html=True,
    )


def _delete_button(label: str, key: str) -> bool:
    return st.button(label, key=key, help=f"Remove this {label.lower()}")


def _form_label(text: str) -> None:
    st.markdown(
        f"<p style='font-size:12px; opacity:0.55; margin:0 0 4px;'>{text}</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_candidate_form(selected_candidate_id: int | None) -> None:
    current_data = {}
    if selected_candidate_id:
        res = run_query(
            "SELECT * FROM candidate WHERE id = %s", (selected_candidate_id,)
        )
        if res:
            current_data = res[0]

    with st.expander("Candidate details", expanded=not bool(selected_candidate_id)):
        with st.form("candidate_details_form", clear_on_submit=False):

            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Basic information</p>",
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns(3)
            full_name = c1.text_input(
                "Full name", value=current_data.get("full_name", "")
            )
            email = c2.text_input(
                "Email", value=current_data.get("email", "")
            )
            phone = c3.text_input(
                "Phone", value=current_data.get("phone", "")
            )

            _divider()
            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Links</p>",
                unsafe_allow_html=True,
            )
            c4, c5, c6 = st.columns(3)
            linkedin  = c4.text_input("LinkedIn URL",  value=current_data.get("linkedin_url", ""))
            github    = c5.text_input("GitHub URL",    value=current_data.get("github_url", ""))
            portfolio = c6.text_input("Portfolio URL", value=current_data.get("portfolio_url", ""))

            _divider()
            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Objective and summary</p>",
                unsafe_allow_html=True,
            )
            career_obj = st.text_area(
                "Career objective",
                value=current_data.get("career_objective", ""),
                height=80,
            )
            current_sum_text = "\n".join(
                _load_json_field(current_data.get("professional_summary"))
            )
            prof_summary = st.text_area(
                "Professional summary — one bullet per line",
                value=current_sum_text,
                height=100,
            )

            submitted = st.form_submit_button(
                "Save candidate", use_container_width=True
            )
            if submitted:
                if full_name and email:
                    summary_bullets = [
                        b.strip() for b in prof_summary.split("\n") if b.strip()
                    ]
                    if selected_candidate_id is None:
                        run_query(
                            """INSERT INTO candidate
                               (full_name, email, phone, linkedin_url, github_url,
                                portfolio_url, career_objective, professional_summary)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (full_name, email, phone, linkedin, github, portfolio,
                             career_obj, json.dumps(summary_bullets)),
                            fetch_results=False,
                        )
                        st.success(f"Candidate '{full_name}' created.")
                    else:
                        run_query(
                            """UPDATE candidate SET
                               full_name=%s, email=%s, phone=%s,
                               linkedin_url=%s, github_url=%s, portfolio_url=%s,
                               career_objective=%s, professional_summary=%s,
                               updated_at=CURRENT_TIMESTAMP
                               WHERE id=%s""",
                            (full_name, email, phone, linkedin, github, portfolio,
                             career_obj, json.dumps(summary_bullets),
                             selected_candidate_id),
                            fetch_results=False,
                        )
                        st.success(f"Candidate '{full_name}' updated.")
                    st.rerun()
                else:
                    st.error("Full name and email are required.")


def _render_skills(candidate_id: int) -> None:
    skills = run_query(
        "SELECT * FROM technical_skills WHERE candidate_id = %s", (candidate_id,)
    )
    with st.expander("Technical skills", expanded=False):
        _section_header("Existing categories", count=len(skills))
        if skills:
            for s in skills:
                skill_list = _load_json_field(s["skills_list"])
                c1, c2 = st.columns([11, 1])
                with c1:
                    pills = "".join([
                        f"""<span style="
                            display:inline-block; font-size:11px;
                            padding:2px 8px; border-radius:10px;
                            border:1px solid rgba(128,128,128,0.2);
                            margin:0 4px 4px 0; opacity:0.75;
                        ">{sk}</span>"""
                        for sk in skill_list
                    ])
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 4px;'>"
                        f"{s['category']}</p>"
                        f"<div style='margin-bottom:8px;'>{pills}</div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Remove", key=f"del_skill_{s['id']}"):
                        run_query(
                            "DELETE FROM technical_skills WHERE id = %s",
                            (s["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No skill categories added yet.")

        _section_header("Add category")
        with st.form("add_skill_form", clear_on_submit=True):
            category    = st.text_input("Category", placeholder="e.g. Backend Technologies")
            skills_input = st.text_area("Skills — comma separated", height=68)
            if st.form_submit_button("Add skills", use_container_width=True):
                if category and skills_input:
                    skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
                    run_query(
                        "INSERT INTO technical_skills (candidate_id, category, skills_list) VALUES (%s,%s,%s)",
                        (candidate_id, category, json.dumps(skills_list)),
                        fetch_results=False,
                    )
                    st.rerun()


def _render_experience(candidate_id: int) -> None:
    experiences = run_query(
        "SELECT * FROM work_experience WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST",
        (candidate_id,),
    )
    with st.expander("Work experience", expanded=False):
        _section_header("Positions", count=len(experiences))
        if experiences:
            for e in experiences:
                c1, c2 = st.columns([11, 1])
                with c1:
                    tech_list = _load_json_field(e.get("technologies_utilized"))
                    end = e.get("end_date") or "Present"
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 2px;'>"
                        f"{e['role_title']} — {e['company_name']}</p>"
                        f"<p style='font-size:12px; opacity:0.45; margin:0 0 6px;'>"
                        f"{e.get('start_date', '')} to {end}</p>",
                        unsafe_allow_html=True,
                    )
                    if tech_list:
                        pills = "".join([
                            f"""<span style="
                                display:inline-block; font-size:11px;
                                padding:2px 8px; border-radius:10px;
                                border:1px solid rgba(128,128,128,0.2);
                                margin:0 4px 4px 0; opacity:0.65;
                            ">{t}</span>"""
                            for t in tech_list
                        ])
                        st.markdown(
                            f"<div style='margin-bottom:4px;'>{pills}</div>",
                            unsafe_allow_html=True,
                        )
                with c2:
                    if st.button("Remove", key=f"del_exp_{e['id']}"):
                        run_query(
                            "DELETE FROM work_experience WHERE id = %s",
                            (e["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No work experience added yet.")

        _section_header("Add position")
        with st.form("add_exp_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company    = c1.text_input("Company name")
            role       = c2.text_input("Role title")
            start_date = c1.date_input("Start date")
            end_date   = c2.date_input("End date — leave as-is for present", value=None)
            bullets    = st.text_area("Contributions — one bullet per line", height=80)
            tech_used  = st.text_input("Technologies — comma separated")
            if st.form_submit_button("Add experience", use_container_width=True):
                if company and role:
                    bullet_list = [b.strip() for b in bullets.split("\n") if b.strip()]
                    tech_list   = [t.strip() for t in tech_used.split(",") if t.strip()]
                    run_query(
                        """INSERT INTO work_experience
                           (candidate_id, company_name, role_title, start_date, end_date,
                            role_and_contributions, technologies_utilized)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (candidate_id, company, role, start_date, end_date,
                         json.dumps(bullet_list), json.dumps(tech_list)),
                        fetch_results=False,
                    )
                    st.rerun()


def _render_education(candidate_id: int) -> None:
    education = run_query(
        "SELECT * FROM education WHERE candidate_id = %s ORDER BY end_year DESC NULLS FIRST",
        (candidate_id,),
    )
    with st.expander("Education", expanded=False):
        _section_header("Degrees", count=len(education))
        if education:
            for ed in education:
                c1, c2 = st.columns([11, 1])
                with c1:
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 2px;'>"
                        f"{ed['degree']} in {ed['field_of_study']}</p>"
                        f"<p style='font-size:12px; opacity:0.45; margin:0;'>"
                        f"{ed['institution']}, {ed['location']} "
                        f"({ed['start_year']} – {ed['end_year']})</p>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Remove", key=f"del_edu_{ed['id']}"):
                        run_query(
                            "DELETE FROM education WHERE id = %s",
                            (ed["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No education added yet.")

        _section_header("Add degree")
        with st.form("add_edu_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            degree   = c1.text_input("Degree", placeholder="e.g. M.Sc.")
            field    = c1.text_input("Field of study")
            inst     = c2.text_input("Institution")
            loc      = c2.text_input("Location")
            start_yr = c1.number_input("Start year", min_value=1950, max_value=2100, step=1, value=2018)
            end_yr   = c2.number_input("End year",   min_value=1950, max_value=2100, step=1, value=2020)
            if st.form_submit_button("Add education", use_container_width=True):
                if degree and inst:
                    run_query(
                        """INSERT INTO education
                           (candidate_id, degree, field_of_study, institution,
                            location, start_year, end_year)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (candidate_id, degree, field, inst, loc, start_yr, end_yr),
                        fetch_results=False,
                    )
                    st.rerun()


def _render_projects(candidate_id: int) -> None:
    projects = run_query(
        "SELECT * FROM projects WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST",
        (candidate_id,),
    )
    with st.expander("Projects", expanded=False):
        _section_header("Portfolio", count=len(projects))
        if projects:
            for p in projects:
                c1, c2 = st.columns([11, 1])
                with c1:
                    tech_list = _load_json_field(p.get("technologies_utilized"))
                    url_html  = (
                        f"<a href='{p['project_url']}' target='_blank' "
                        f"style='font-size:12px; opacity:0.55;'>View project</a>"
                        if p.get("project_url") else ""
                    )
                    pills = "".join([
                        f"""<span style="
                            display:inline-block; font-size:11px;
                            padding:2px 8px; border-radius:10px;
                            border:1px solid rgba(128,128,128,0.2);
                            margin:0 4px 4px 0; opacity:0.65;
                        ">{t}</span>"""
                        for t in tech_list
                    ])
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 2px;'>"
                        f"{p['project_name']}</p>"
                        f"<div style='margin-bottom:4px;'>{pills}</div>"
                        f"{url_html}",
                        unsafe_allow_html=True,
                    )
                    if p.get("description"):
                        st.markdown(
                            f"<p style='font-size:12px; opacity:0.6; margin-top:4px;'>"
                            f"{p['description']}</p>",
                            unsafe_allow_html=True,
                        )
                with c2:
                    if st.button("Remove", key=f"del_proj_{p['id']}"):
                        run_query(
                            "DELETE FROM projects WHERE id = %s",
                            (p["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No projects added yet.")

        _section_header("Add project")
        with st.form("add_proj_form", clear_on_submit=True):
            c1, c2   = st.columns(2)
            proj_name = c1.text_input("Project name")
            proj_url  = c2.text_input("Project URL — optional")
            start_date = c1.date_input("Start date", key="proj_start")
            end_date   = c2.date_input("End date — leave as-is for ongoing", value=None, key="proj_end")
            tech_used  = st.text_input("Technologies — comma separated")
            desc       = st.text_area("Description", height=68)
            if st.form_submit_button("Add project", use_container_width=True):
                if proj_name:
                    tech_list = [t.strip() for t in tech_used.split(",") if t.strip()]
                    run_query(
                        """INSERT INTO projects
                           (candidate_id, project_name, description, technologies_utilized,
                            project_url, start_date, end_date)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (candidate_id, proj_name, desc, json.dumps(tech_list),
                         proj_url, start_date, end_date),
                        fetch_results=False,
                    )
                    st.rerun()


def _render_certifications(candidate_id: int) -> None:
    certs = run_query(
        "SELECT * FROM certifications WHERE candidate_id = %s ORDER BY issue_date DESC NULLS FIRST",
        (candidate_id,),
    )
    with st.expander("Certifications", expanded=False):
        _section_header("Credentials", count=len(certs))
        if certs:
            for c in certs:
                c1, c2 = st.columns([11, 1])
                with c1:
                    expiry = c.get("expiration_date") or "No expiration"
                    url_html = (
                        f"<a href='{c['credential_url']}' target='_blank' "
                        f"style='font-size:12px; opacity:0.55;'>View credential</a>"
                        if c.get("credential_url") else ""
                    )
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 2px;'>"
                        f"{c['certificate_name']}</p>"
                        f"<p style='font-size:12px; opacity:0.45; margin:0 0 4px;'>"
                        f"{c['issuing_organization']} &middot; "
                        f"Issued {c['issue_date']} &middot; Expires {expiry}</p>"
                        f"{url_html}",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Remove", key=f"del_cert_{c['id']}"):
                        run_query(
                            "DELETE FROM certifications WHERE id = %s",
                            (c["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No certifications added yet.")

        _section_header("Add certification")
        with st.form("add_cert_form", clear_on_submit=True):
            c1, c2    = st.columns(2)
            cert_name = c1.text_input("Certificate name")
            org       = c2.text_input("Issuing organization")
            issue_date = c1.date_input("Issue date", key="cert_issue")
            exp_date   = c2.date_input("Expiration date — optional", value=None, key="cert_exp")
            cred_url   = st.text_input("Credential URL — optional")
            if st.form_submit_button("Add certification", use_container_width=True):
                if cert_name and org:
                    run_query(
                        """INSERT INTO certifications
                           (candidate_id, certificate_name, issuing_organization,
                            issue_date, expiration_date, credential_url)
                           VALUES (%s,%s,%s,%s,%s,%s)""",
                        (candidate_id, cert_name, org, issue_date, exp_date, cred_url),
                        fetch_results=False,
                    )
                    st.rerun()


# ---------------------------------------------------------------------------
# Page entry point
# ---------------------------------------------------------------------------

def render_master_profile() -> None:

    # ── Page header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 1.25rem;">
            <p style="font-size:22px; font-weight:600; margin:0; line-height:1.3;">
                Master Profile
            </p>
            <p style="font-size:13px; opacity:0.5; margin:4px 0 0;">
                Manage candidate profiles, skills, experience, and credentials
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Candidate selector ───────────────────────────────────────
    profiles = run_query("SELECT id, full_name FROM candidate ORDER BY id")
    profile_options = {"Create new candidate": None}
    for p in profiles:
        name = p["full_name"] or f"Unnamed (ID {p['id']})"
        profile_options[name] = p["id"]

    selected_option      = st.selectbox(
        "Candidate",
        list(profile_options.keys()),
        label_visibility="collapsed",
    )
    selected_candidate_id = profile_options[selected_option]

    # Store active candidate name in session for the header avatar
    if selected_candidate_id:
        st.session_state["active_candidate_name"] = selected_option

    _divider()

    # ── Candidate details form ───────────────────────────────────
    _render_candidate_form(selected_candidate_id)

    if not selected_candidate_id:
        st.markdown(
            "<p style='font-size:13px; opacity:0.4; margin-top:1rem;'>"
            "Select or create a candidate above to manage their profile sections.</p>",
            unsafe_allow_html=True,
        )
        return

    # ── Active candidate label ───────────────────────────────────
    st.markdown(
        f"""
        <div style="
            display:flex; align-items:center; gap:8px;
            padding:10px 14px;
            border-radius:8px;
            border:1px solid rgba(128,128,128,0.15);
            margin:1rem 0;
            font-size:13px;
        ">
            <div style="
                width:24px; height:24px; border-radius:50%;
                background:#185FA5; color:#E6F1FB;
                font-size:10px; font-weight:600;
                display:flex; align-items:center; justify-content:center;
                flex-shrink:0;
            ">{"".join(w[0].upper() for w in selected_option.split()[:2])}</div>
            <span>Managing profile for <strong>{selected_option}</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Profile sections ─────────────────────────────────────────
    _render_skills(selected_candidate_id)
    _render_experience(selected_candidate_id)
    _render_education(selected_candidate_id)
    _render_projects(selected_candidate_id)
    _render_certifications(selected_candidate_id)