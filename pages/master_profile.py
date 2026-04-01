"""Master Profile: Multi-Candidate Management with full Add/Remove capabilities."""
import streamlit as st
import json
from data.db_utils import run_query

def render_master_profile():
    st.subheader("Candidate Master Profiles")
    
    # --- 1. CANDIDATE SELECTOR ---
    profiles = run_query("SELECT id, full_name FROM candidate ORDER BY id")
    
    # Dropdown options: "Create New Candidate..." plus existing names
    profile_options = {"Create New Candidate...": None}
    for p in profiles:
        display_name = p['full_name'] if p['full_name'] else f"Unnamed Candidate (ID: {p['id']})"
        profile_options[display_name] = p['id']
        
    selected_option = st.selectbox("Select Candidate", list(profile_options.keys()))
    selected_candidate_id = profile_options[selected_option]

    # --- 2. CANDIDATE DETAILS & SUMMARY ---
    with st.expander("Candidate Details & Summary", expanded=True if not selected_candidate_id else False):
        current_data = {}
        if selected_candidate_id:
            res = run_query("SELECT * FROM candidate WHERE id = %s", (selected_candidate_id,))
            if res:
                current_data = res[0]
        
        with st.form("candidate_details_form", clear_on_submit=False):
            st.markdown("#### Basic Information")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                full_name = st.text_input("Full Name (e.g., Prashanth, Karthik, Ganesh)", value=current_data.get('full_name', ''))
            with c2:
                email = st.text_input("Email", value=current_data.get('email', ''))
            with c3:
                phone = st.text_input("Phone", value=current_data.get('phone', ''))
                
            st.markdown("#### Links")
            c4, c5, c6 = st.columns(3)
            with c4:
                linkedin = st.text_input("LinkedIn URL", value=current_data.get('linkedin_url', ''))
            with c5:
                github = st.text_input("GitHub URL", value=current_data.get('github_url', ''))
            with c6:
                portfolio = st.text_input("Portfolio URL", value=current_data.get('portfolio_url', ''))

            st.markdown("#### Objective & Summary")
            career_obj = st.text_area("Career Objective", value=current_data.get('career_objective', ''))
            
            current_sum_list = []
            if current_data.get('professional_summary'):
                summary_data = current_data['professional_summary']
                current_sum_list = summary_data if isinstance(summary_data, list) else json.loads(summary_data)
            current_sum_text = "\n".join(current_sum_list)
            
            prof_summary = st.text_area("Professional Summary (One bullet per line)", value=current_sum_text)
            
            if st.form_submit_button("Save Candidate Details", type="primary"):
                if full_name and email:
                    summary_bullets = [b.strip() for b in prof_summary.split("\n") if b.strip()]
                    
                    if selected_candidate_id is None:
                        # INSERT NEW CANDIDATE
                        run_query(
                            """INSERT INTO candidate 
                               (full_name, email, phone, linkedin_url, github_url, portfolio_url, career_objective, professional_summary) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                            (full_name, email, phone, linkedin, github, portfolio, career_obj, json.dumps(summary_bullets)),
                            fetch_results=False
                        )
                        st.success(f"New candidate '{full_name}' created!")
                    else:
                        # UPDATE EXISTING CANDIDATE
                        run_query(
                            """UPDATE candidate SET 
                               full_name = %s, email = %s, phone = %s, 
                               linkedin_url = %s, github_url = %s, portfolio_url = %s, 
                               career_objective = %s, professional_summary = %s, updated_at = CURRENT_TIMESTAMP
                               WHERE id = %s""",
                            (full_name, email, phone, linkedin, github, portfolio, career_obj, json.dumps(summary_bullets), selected_candidate_id),
                            fetch_results=False
                        )
                        st.success(f"Candidate '{full_name}' updated!")
                    st.rerun()
                else:
                    st.error("Full Name and Email are required.")

    if not selected_candidate_id:
        st.info("Please select or create a candidate above to manage their Skills, Experience, and Education.")
        return

    st.divider()
    st.markdown(f"### Managing Data for: {selected_option}")

    # --- 3. TECHNICAL SKILLS ---
    with st.expander("Technical Skills", expanded=False):
        skills = run_query("SELECT * FROM technical_skills WHERE candidate_id = %s", (selected_candidate_id,))
        if skills:
            for s in skills:
                col1, col2 = st.columns([10, 1])
                with col1:
                    skill_list = s['skills_list'] if isinstance(s['skills_list'], list) else json.loads(s['skills_list'])
                    st.markdown(f"**{s['category']}**: {', '.join(skill_list)}")
                with col2:
                    if st.button("❌", key=f"del_skill_{s['id']}", help="Delete this skill category"):
                        run_query("DELETE FROM technical_skills WHERE id = %s", (s['id'],), fetch_results=False)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No skills added.")
            
        with st.form("add_skill_form", clear_on_submit=True):
            category = st.text_input("Category (e.g., Backend Technologies)")
            skills_input = st.text_area("Skills (comma-separated)")
            if st.form_submit_button("Add Skills"):
                if category and skills_input:
                    skills_list = [s.strip() for s in skills_input.split(",")]
                    run_query(
                        "INSERT INTO technical_skills (candidate_id, category, skills_list) VALUES (%s, %s, %s)",
                        (selected_candidate_id, category, json.dumps(skills_list)), fetch_results=False
                    )
                    st.rerun()

    # --- 4. WORK EXPERIENCE ---
    with st.expander("Work Experience", expanded=False):
        experiences = run_query(
            "SELECT * FROM work_experience WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST", 
            (selected_candidate_id,)
        )
        if experiences:
            for e in experiences:
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"**{e['role_title']}** at **{e['company_name']}**")
                    tech = e.get('technologies_utilized')
                    if tech:
                        tech_list = tech if isinstance(tech, list) else json.loads(tech)
                        st.caption(f"Technologies: {', '.join(tech_list)}")
                with col2:
                    if st.button("❌", key=f"del_exp_{e['id']}", help="Delete experience"):
                        run_query("DELETE FROM work_experience WHERE id = %s", (e['id'],), fetch_results=False)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No work experience added.")
            
        with st.form("add_exp_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company Name")
            role = c2.text_input("Role Title")
            start_date = c1.date_input("Start Date")
            end_date = c2.date_input("End Date (Leave blank for Present)", value=None)
            bullets = st.text_area("Role & Contributions (One bullet per line)")
            tech_used = st.text_input("Technologies Utilized (comma-separated)")
            if st.form_submit_button("Add Experience"):
                if company and role:
                    bullet_list = [b.strip() for b in bullets.split("\n") if b.strip()]
                    tech_list = [t.strip() for t in tech_used.split(",")] if tech_used else []
                    run_query(
                        """INSERT INTO work_experience 
                           (candidate_id, company_name, role_title, start_date, end_date, role_and_contributions, technologies_utilized) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (selected_candidate_id, company, role, start_date, end_date, json.dumps(bullet_list), json.dumps(tech_list)),
                        fetch_results=False
                    )
                    st.rerun()

    # --- 5. EDUCATION ---
    with st.expander("Education", expanded=False):
        education = run_query(
            "SELECT * FROM education WHERE candidate_id = %s ORDER BY end_year DESC NULLS FIRST", 
            (selected_candidate_id,)
        )
        if education:
            for ed in education:
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"**{ed['degree']}** in {ed['field_of_study']}")
                    st.caption(f"{ed['institution']}, {ed['location']} ({ed['start_year']} - {ed['end_year']})")
                with col2:
                    if st.button("❌", key=f"del_edu_{ed['id']}", help="Delete education"):
                        run_query("DELETE FROM education WHERE id = %s", (ed['id'],), fetch_results=False)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No education added.")
            
        with st.form("add_edu_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            degree = c1.text_input("Degree (e.g., M.Sc.)")
            field = c1.text_input("Field of Study")
            inst = c2.text_input("Institution")
            loc = c2.text_input("Location")
            start_yr = c1.number_input("Start Year", min_value=1950, max_value=2100, step=1, value=2018)
            end_yr = c2.number_input("End Year", min_value=1950, max_value=2100, step=1, value=2020)
            if st.form_submit_button("Add Education"):
                if degree and inst:
                    run_query(
                        """INSERT INTO education (candidate_id, degree, field_of_study, institution, location, start_year, end_year) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (selected_candidate_id, degree, field, inst, loc, start_yr, end_yr), fetch_results=False
                    )
                    st.rerun()

    # --- 6. PROJECTS (Optional) ---
    with st.expander("Projects", expanded=False):
        projects = run_query(
            "SELECT * FROM projects WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST", 
            (selected_candidate_id,)
        )
        if projects:
            for p in projects:
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"**{p['project_name']}**")
                    if p.get('project_url'):
                        st.markdown(f"[Link to Project]({p['project_url']})")
                    
                    tech = p.get('technologies_utilized')
                    if tech:
                        tech_list = tech if isinstance(tech, list) else json.loads(tech)
                        st.caption(f"Technologies: {', '.join(tech_list)}")
                    
                    if p.get('description'):
                        st.write(p['description'])
                with col2:
                    if st.button("❌", key=f"del_proj_{p['id']}", help="Delete project"):
                        run_query("DELETE FROM projects WHERE id = %s", (p['id'],), fetch_results=False)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No standalone projects added.")
            
        with st.form("add_proj_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            proj_name = c1.text_input("Project Name")
            proj_url = c2.text_input("Project URL (Optional)")
            start_date = c1.date_input("Start Date", key="proj_start")
            end_date = c2.date_input("End Date (Leave blank for Ongoing)", value=None, key="proj_end")
            
            tech_used = st.text_input("Technologies Utilized (comma-separated)")
            desc = st.text_area("Description")
            
            if st.form_submit_button("Add Project"):
                if proj_name:
                    tech_list = [t.strip() for t in tech_used.split(",")] if tech_used else []
                    run_query(
                        """INSERT INTO projects (candidate_id, project_name, description, technologies_utilized, project_url, start_date, end_date) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (selected_candidate_id, proj_name, desc, json.dumps(tech_list), proj_url, start_date, end_date), 
                        fetch_results=False
                    )
                    st.rerun()

    # --- 7. CERTIFICATIONS (Optional) ---
    with st.expander("Certifications", expanded=False):
        certs = run_query(
            "SELECT * FROM certifications WHERE candidate_id = %s ORDER BY issue_date DESC NULLS FIRST", 
            (selected_candidate_id,)
        )
        if certs:
            for c in certs:
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"**{c['certificate_name']}** — {c['issuing_organization']}")
                    if c.get('credential_url'):
                        st.markdown(f"[View Credential]({c['credential_url']})")
                    st.caption(f"Issued: {c['issue_date']} | Expires: {c['expiration_date'] if c['expiration_date'] else 'No Expiration'}")
                with col2:
                    if st.button("❌", key=f"del_cert_{c['id']}", help="Delete certification"):
                        run_query("DELETE FROM certifications WHERE id = %s", (c['id'],), fetch_results=False)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No certifications added.")
            
        with st.form("add_cert_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cert_name = c1.text_input("Certificate Name")
            org = c2.text_input("Issuing Organization")
            issue_date = c1.date_input("Issue Date", key="cert_issue")
            exp_date = c2.date_input("Expiration Date (Optional)", value=None, key="cert_exp")
            cred_url = st.text_input("Credential URL (Optional)")
            
            if st.form_submit_button("Add Certification"):
                if cert_name and org:
                    run_query(
                        """INSERT INTO certifications (candidate_id, certificate_name, issuing_organization, issue_date, expiration_date, credential_url) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (selected_candidate_id, cert_name, org, issue_date, exp_date, cred_url), 
                        fetch_results=False
                    )
                    st.rerun()