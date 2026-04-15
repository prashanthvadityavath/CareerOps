"""Master Profile: multi-candidate management with full CRUD."""
import streamlit as st
import json
import time
from data.db_utils import run_query


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _load_json_field(value) -> list:
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
            cand_prefix = f"cand_{selected_candidate_id or 'new'}"

            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Basic information</p>",
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns(3)
            full_name = c1.text_input("Full name", value=current_data.get("full_name", ""), key=f"{cand_prefix}_fn")
            email     = c2.text_input("Email",     value=current_data.get("email", ""),     key=f"{cand_prefix}_em")
            phone     = c3.text_input("Phone",     value=current_data.get("phone", ""),     key=f"{cand_prefix}_ph")

            _divider()
            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Links</p>",
                unsafe_allow_html=True,
            )
            c4, c5, c6 = st.columns(3)
            linkedin  = c4.text_input("LinkedIn URL",  value=current_data.get("linkedin_url", ""),  key=f"{cand_prefix}_li")
            github    = c5.text_input("GitHub URL",    value=current_data.get("github_url", ""),    key=f"{cand_prefix}_gh")
            portfolio = c6.text_input("Portfolio URL", value=current_data.get("portfolio_url", ""), key=f"{cand_prefix}_po")

            _divider()
            st.markdown(
                "<p style='font-size:13px; font-weight:500; margin-bottom:12px;'>Objective and summary</p>",
                unsafe_allow_html=True,
            )
            career_obj = st.text_area(
                "Career objective",
                value=current_data.get("career_objective", ""),
                height=80,
                key=f"{cand_prefix}_co",
            )
            current_sum_text = "\n".join(
                _load_json_field(current_data.get("professional_summary"))
            )
            prof_summary = st.text_area(
                "Professional summary — one bullet per line",
                value=current_sum_text,
                height=100,
                key=f"{cand_prefix}_ps",
            )

            submitted = st.form_submit_button("Save candidate", use_container_width=True)

            if submitted:
                if full_name and email:
                    summary_bullets = [
                        b.strip() for b in prof_summary.split("\n") if b.strip()
                    ]

                    if selected_candidate_id is None:
                        existing = run_query(
                            "SELECT id FROM candidate WHERE email = %s", (email,)
                        )
                    else:
                        existing = run_query(
                            "SELECT id FROM candidate WHERE email = %s AND id != %s",
                            (email, selected_candidate_id),
                        )

                    if existing:
                        st.warning("A candidate with this email already exists.")
                    else:
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
                            st.success("candidate profile created successfully")
                            st.session_state["pending_candidate_select"] = full_name
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
                            st.success("candidate profile updated successfully")
                            st.session_state["pending_candidate_select"] = full_name
                        time.sleep(1.5)
                        st.rerun()
                else:
                    st.error("Full name and email are required.")


def _render_skills(candidate_id: int) -> None:
    skills = run_query(
        "SELECT * FROM technical_skills WHERE candidate_id = %s", (candidate_id,)
    )
    edit_skill_id = st.session_state.get("edit_skill_id")

    with st.expander("Technical skills", expanded=False):
        _section_header("Existing categories", count=len(skills))
        if skills:
            for s in skills:
                skill_list = _load_json_field(s["skills_list"])
                c1, c2, c3 = st.columns([10, 1, 1])
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
                    if st.button("Edit", key=f"ed_sk_{s['id']}"):
                        st.session_state["edit_skill_id"] = s["id"]
                        st.rerun()
                with c3:
                    if st.button("Remove", key=f"del_sk_{s['id']}"):
                        run_query(
                            "DELETE FROM technical_skills WHERE id = %s",
                            (s["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No skill categories added yet.")

        edit_data = next((item for item in skills if item["id"] == edit_skill_id), None) if edit_skill_id else None
        _section_header("Edit category" if edit_skill_id else "Add category")

        with st.form("add_skill_form", clear_on_submit=True):
            sk_prefix    = f"sk_{edit_skill_id or 'new'}"
            cat_val      = edit_data["category"] if edit_data else ""
            skills_val   = ", ".join(_load_json_field(edit_data["skills_list"])) if edit_data else ""
            category     = st.text_input("Category", value=cat_val, placeholder="e.g. Backend Technologies", key=f"{sk_prefix}_cat")
            skills_input = st.text_area("Skills — comma separated", value=skills_val, height=68, key=f"{sk_prefix}_val")
            fc1, fc2 = st.columns(2)
            with fc1:
                if st.form_submit_button("Update skills" if edit_skill_id else "Add skills", use_container_width=True):
                    if category and skills_input:
                        skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
                        if edit_skill_id:
                            run_query(
                                "UPDATE technical_skills SET category=%s, skills_list=%s WHERE id=%s",
                                (category, json.dumps(skills_list), edit_skill_id),
                                fetch_results=False,
                            )
                            st.session_state.pop("edit_skill_id", None)
                        else:
                            run_query(
                                "INSERT INTO technical_skills (candidate_id, category, skills_list) VALUES (%s,%s,%s)",
                                (candidate_id, category, json.dumps(skills_list)),
                                fetch_results=False,
                            )
                        st.rerun()
            with fc2:
                if edit_skill_id and st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("edit_skill_id", None)
                    st.rerun()


def _render_experience(candidate_id: int) -> None:
    experiences = run_query(
        "SELECT * FROM work_experience WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST",
        (candidate_id,),
    )
    edit_exp_id = st.session_state.get("edit_exp_id")

    with st.expander("Work experience", expanded=False):
        _section_header("Positions", count=len(experiences))
        if experiences:
            for e in experiences:
                c1, c2, c3 = st.columns([10, 1, 1])
                with c1:
                    tech_list   = _load_json_field(e.get("technologies_utilized"))
                    bullet_list = _load_json_field(e.get("role_and_contributions"))
                    end = e.get("end_date") or "Present"
                    st.markdown(
                        f"<p style='font-size:13px; font-weight:500; margin:0 0 2px;'>"
                        f"{e['role_title']} — {e['company_name']}</p>"
                        f"<p style='font-size:12px; opacity:0.45; margin:0 0 6px;'>"
                        f"{e.get('start_date', '')} to {end}</p>",
                        unsafe_allow_html=True,
                    )
                    if bullet_list:
                        bullets_html = "".join([
                            f"<li style='font-size:12px; opacity:0.75; margin-bottom:2px;'>{b}</li>"
                            for b in bullet_list
                        ])
                        st.markdown(
                            f"<ul style='margin-top:4px; margin-bottom:8px; padding-left:20px;'>{bullets_html}</ul>",
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
                        st.markdown(f"<div style='margin-bottom:4px;'>{pills}</div>", unsafe_allow_html=True)
                with c2:
                    if st.button("Edit", key=f"ed_exp_{e['id']}"):
                        st.session_state["edit_exp_id"] = e["id"]
                        st.rerun()
                with c3:
                    if st.button("Remove", key=f"del_exp_{e['id']}"):
                        run_query(
                            "DELETE FROM work_experience WHERE id = %s",
                            (e["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No work experience added yet.")

        edit_data = next((item for item in experiences if item["id"] == edit_exp_id), None) if edit_exp_id else None
        _section_header("Edit position" if edit_exp_id else "Add position")

        with st.form("add_exp_form", clear_on_submit=True):
            exp_prefix = f"exp_{edit_exp_id or 'new'}"
            c1, c2     = st.columns(2)
            company    = c1.text_input("Company name", value=edit_data["company_name"] if edit_data else "", key=f"{exp_prefix}_comp")
            role       = c2.text_input("Role title",   value=edit_data["role_title"]   if edit_data else "", key=f"{exp_prefix}_role")
            start_date = c1.date_input("Start date", value=edit_data["start_date"] if edit_data and edit_data["start_date"] else "today", key=f"{exp_prefix}_sd")
            end_date   = c2.date_input("End date — leave as-is for present", value=edit_data["end_date"] if edit_data else None, key=f"{exp_prefix}_ed")
            b_val      = "\n".join(_load_json_field(edit_data.get("role_and_contributions"))) if edit_data else ""
            t_val      = ", ".join(_load_json_field(edit_data.get("technologies_utilized"))) if edit_data else ""
            bullets    = st.text_area("Contributions — one bullet per line", value=b_val, height=80, key=f"{exp_prefix}_bul")
            tech_used  = st.text_input("Technologies — comma separated", value=t_val, key=f"{exp_prefix}_tech")
            fc1, fc2   = st.columns(2)
            with fc1:
                if st.form_submit_button("Update experience" if edit_exp_id else "Add experience", use_container_width=True):
                    if company and role:
                        bullet_list = [b.strip() for b in bullets.split("\n") if b.strip()]
                        tech_list   = [t.strip() for t in tech_used.split(",") if t.strip()]
                        if edit_exp_id:
                            run_query(
                                """UPDATE work_experience SET
                                   company_name=%s, role_title=%s, start_date=%s, end_date=%s,
                                   role_and_contributions=%s, technologies_utilized=%s
                                   WHERE id=%s""",
                                (company, role, start_date, end_date,
                                 json.dumps(bullet_list), json.dumps(tech_list), edit_exp_id),
                                fetch_results=False,
                            )
                            st.session_state.pop("edit_exp_id", None)
                        else:
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
            with fc2:
                if edit_exp_id and st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("edit_exp_id", None)
                    st.rerun()


def _render_education(candidate_id: int) -> None:
    education = run_query(
        "SELECT * FROM education WHERE candidate_id = %s ORDER BY end_year DESC NULLS FIRST",
        (candidate_id,),
    )
    edit_edu_id = st.session_state.get("edit_edu_id")

    with st.expander("Education", expanded=False):
        _section_header("Degrees", count=len(education))
        if education:
            for ed in education:
                c1, c2, c3 = st.columns([10, 1, 1])
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
                    if st.button("Edit", key=f"ed_edu_{ed['id']}"):
                        st.session_state["edit_edu_id"] = ed["id"]
                        st.rerun()
                with c3:
                    if st.button("Remove", key=f"del_edu_{ed['id']}"):
                        run_query(
                            "DELETE FROM education WHERE id = %s",
                            (ed["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No education added yet.")

        edit_data = next((item for item in education if item["id"] == edit_edu_id), None) if edit_edu_id else None
        _section_header("Edit degree" if edit_edu_id else "Add degree")

        with st.form("add_edu_form", clear_on_submit=True):
            edu_prefix = f"edu_{edit_edu_id or 'new'}"
            c1, c2   = st.columns(2)
            degree   = c1.text_input("Degree", value=edit_data["degree"] if edit_data else "", placeholder="e.g. M.Sc.", key=f"{edu_prefix}_deg")
            field    = c1.text_input("Field of study", value=edit_data["field_of_study"] if edit_data else "", key=f"{edu_prefix}_fld")
            inst     = c2.text_input("Institution", value=edit_data["institution"] if edit_data else "", key=f"{edu_prefix}_inst")
            loc      = c2.text_input("Location", value=edit_data["location"] if edit_data else "", key=f"{edu_prefix}_loc")
            start_yr = c1.number_input("Start year", min_value=1950, max_value=2100, step=1, value=edit_data["start_year"] if edit_data else 2018, key=f"{edu_prefix}_sy")
            end_yr   = c2.number_input("End year",   min_value=1950, max_value=2100, step=1, value=edit_data["end_year"]   if edit_data else 2020, key=f"{edu_prefix}_ey")
            fc1, fc2 = st.columns(2)
            with fc1:
                if st.form_submit_button("Update education" if edit_edu_id else "Add education", use_container_width=True):
                    if degree and inst:
                        if edit_edu_id:
                            run_query(
                                """UPDATE education SET
                                   degree=%s, field_of_study=%s, institution=%s,
                                   location=%s, start_year=%s, end_year=%s
                                   WHERE id=%s""",
                                (degree, field, inst, loc, start_yr, end_yr, edit_edu_id),
                                fetch_results=False,
                            )
                            st.session_state.pop("edit_edu_id", None)
                        else:
                            run_query(
                                """INSERT INTO education
                                   (candidate_id, degree, field_of_study, institution,
                                    location, start_year, end_year)
                                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                                (candidate_id, degree, field, inst, loc, start_yr, end_yr),
                                fetch_results=False,
                            )
                        st.rerun()
            with fc2:
                if edit_edu_id and st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("edit_edu_id", None)
                    st.rerun()


def _render_projects(candidate_id: int) -> None:
    projects = run_query(
        "SELECT * FROM projects WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST",
        (candidate_id,),
    )
    edit_proj_id = st.session_state.get("edit_proj_id")

    with st.expander("Projects", expanded=False):
        _section_header("Portfolio", count=len(projects))
        if projects:
            for p in projects:
                c1, c2, c3 = st.columns([10, 1, 1])
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
                    if st.button("Edit", key=f"ed_proj_{p['id']}"):
                        st.session_state["edit_proj_id"] = p["id"]
                        st.rerun()
                with c3:
                    if st.button("Remove", key=f"del_proj_{p['id']}"):
                        run_query(
                            "DELETE FROM projects WHERE id = %s",
                            (p["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No projects added yet.")

        edit_data = next((item for item in projects if item["id"] == edit_proj_id), None) if edit_proj_id else None
        _section_header("Edit project" if edit_proj_id else "Add project")

        with st.form("add_proj_form", clear_on_submit=True):
            proj_prefix = f"proj_{edit_proj_id or 'new'}"
            c1, c2      = st.columns(2)
            proj_name   = c1.text_input("Project name", value=edit_data["project_name"] if edit_data else "", key=f"{proj_prefix}_name")
            proj_url    = c2.text_input("Project URL — optional", value=edit_data["project_url"] if edit_data else "", key=f"{proj_prefix}_url")
            start_date  = c1.date_input("Start date", value=edit_data["start_date"] if edit_data and edit_data["start_date"] else "today", key=f"{proj_prefix}_sd")
            end_date    = c2.date_input("End date — leave as-is for ongoing", value=edit_data["end_date"] if edit_data else None, key=f"{proj_prefix}_ed")
            t_val       = ", ".join(_load_json_field(edit_data.get("technologies_utilized"))) if edit_data else ""
            tech_used   = st.text_input("Technologies — comma separated", value=t_val, key=f"{proj_prefix}_tech")
            desc        = st.text_area("Description", value=edit_data["description"] if edit_data else "", height=68, key=f"{proj_prefix}_desc")
            fc1, fc2    = st.columns(2)
            with fc1:
                if st.form_submit_button("Update project" if edit_proj_id else "Add project", use_container_width=True):
                    if proj_name:
                        tech_list = [t.strip() for t in tech_used.split(",") if t.strip()]
                        if edit_proj_id:
                            run_query(
                                """UPDATE projects SET
                                   project_name=%s, description=%s, technologies_utilized=%s,
                                   project_url=%s, start_date=%s, end_date=%s
                                   WHERE id=%s""",
                                (proj_name, desc, json.dumps(tech_list),
                                 proj_url, start_date, end_date, edit_proj_id),
                                fetch_results=False,
                            )
                            st.session_state.pop("edit_proj_id", None)
                        else:
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
            with fc2:
                if edit_proj_id and st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("edit_proj_id", None)
                    st.rerun()


def _render_certifications(candidate_id: int) -> None:
    certs = run_query(
        "SELECT * FROM certifications WHERE candidate_id = %s ORDER BY issue_date DESC NULLS FIRST",
        (candidate_id,),
    )
    edit_cert_id = st.session_state.get("edit_cert_id")

    with st.expander("Certifications", expanded=False):
        _section_header("Credentials", count=len(certs))
        if certs:
            for c in certs:
                c1, c2, c3 = st.columns([10, 1, 1])
                with c1:
                    expiry   = c.get("expiration_date") or "No expiration"
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
                    if st.button("Edit", key=f"ed_cert_{c['id']}"):
                        st.session_state["edit_cert_id"] = c["id"]
                        st.rerun()
                with c3:
                    if st.button("Remove", key=f"del_cert_{c['id']}"):
                        run_query(
                            "DELETE FROM certifications WHERE id = %s",
                            (c["id"],), fetch_results=False,
                        )
                        st.rerun()
                _divider()
        else:
            _empty_state("No certifications added yet.")

        edit_data = next((item for item in certs if item["id"] == edit_cert_id), None) if edit_cert_id else None
        _section_header("Edit certification" if edit_cert_id else "Add certification")

        with st.form("add_cert_form", clear_on_submit=True):
            cert_prefix = f"cert_{edit_cert_id or 'new'}"
            c1, c2      = st.columns(2)
            cert_name   = c1.text_input("Certificate name", value=edit_data["certificate_name"] if edit_data else "", key=f"{cert_prefix}_name")
            org         = c2.text_input("Issuing organization", value=edit_data["issuing_organization"] if edit_data else "", key=f"{cert_prefix}_org")
            issue_date  = c1.date_input("Issue date", value=edit_data["issue_date"] if edit_data and edit_data["issue_date"] else "today", key=f"{cert_prefix}_idate")
            exp_date    = c2.date_input("Expiration date — optional", value=edit_data["expiration_date"] if edit_data else None, key=f"{cert_prefix}_edate")
            cred_url    = st.text_input("Credential URL — optional", value=edit_data["credential_url"] if edit_data else "", key=f"{cert_prefix}_url")
            fc1, fc2    = st.columns(2)
            with fc1:
                if st.form_submit_button("Update certification" if edit_cert_id else "Add certification", use_container_width=True):
                    if cert_name and org:
                        if edit_cert_id:
                            run_query(
                                """UPDATE certifications SET
                                   certificate_name=%s, issuing_organization=%s,
                                   issue_date=%s, expiration_date=%s, credential_url=%s
                                   WHERE id=%s""",
                                (cert_name, org, issue_date, exp_date, cred_url, edit_cert_id),
                                fetch_results=False,
                            )
                            st.session_state.pop("edit_cert_id", None)
                        else:
                            run_query(
                                """INSERT INTO certifications
                                   (candidate_id, certificate_name, issuing_organization,
                                    issue_date, expiration_date, credential_url)
                                   VALUES (%s,%s,%s,%s,%s,%s)""",
                                (candidate_id, cert_name, org, issue_date, exp_date, cred_url),
                                fetch_results=False,
                            )
                        st.rerun()
            with fc2:
                if edit_cert_id and st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("edit_cert_id", None)
                    st.rerun()


# ---------------------------------------------------------------------------
# Page entry point
# ---------------------------------------------------------------------------

def render_master_profile() -> None:

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

    if "pending_candidate_select" in st.session_state:
        st.session_state["candidate_select"] = st.session_state.pop("pending_candidate_select")

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
    _render_candidate_form(selected_candidate_id)

    if not selected_candidate_id:
        st.markdown(
            "<p style='font-size:13px; opacity:0.4; margin-top:1rem;'>"
            "Select or create a candidate above to manage their profile sections.</p>",
            unsafe_allow_html=True,
        )
        return

    initials = "".join(w[0].upper() for w in selected_option.split()[:2])
    st.markdown(
        f"""
        <div style="
            display:flex; align-items:center; gap:8px;
            padding:10px 14px; border-radius:8px;
            border:1px solid rgba(128,128,128,0.15);
            margin:1rem 0; font-size:13px;
        ">
            <div style="
                width:24px; height:24px; border-radius:50%;
                background:#185FA5; color:#E6F1FB;
                font-size:10px; font-weight:600;
                display:flex; align-items:center; justify-content:center;
                flex-shrink:0;
            ">{initials}</div>
            <span>Managing profile for <strong>{selected_option}</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_skills(selected_candidate_id)
    _render_experience(selected_candidate_id)
    _render_education(selected_candidate_id)
    _render_projects(selected_candidate_id)
    _render_certifications(selected_candidate_id)