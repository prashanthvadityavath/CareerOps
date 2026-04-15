"""Transforms PostgreSQL candidate data into a formatted Markdown resume."""
import json

def _load_json(value):
    """Safely parse JSONB fields."""
    if not value:
        return []
    return value if isinstance(value, list) else json.loads(value)

def build_default_resume_text(profile: dict | None) -> str:
    """Formats a candidate profile dictionary into a standard text resume."""
    if not profile:
        return "No candidate selected or data not found."
    
    resume_lines = []
    resume_lines.append(f"# {profile.get('full_name', 'Unnamed Candidate').upper()}")
    
    contact_info = [profile.get('email', ''), profile.get('phone', '')]
    links = [profile.get('linkedin_url', ''), profile.get('github_url', ''), profile.get('portfolio_url', '')]
    
    if any(contact_info):
        resume_lines.append(" | ".join([c for c in contact_info if c]))
    if any(links):
        resume_lines.append(" | ".join([l for l in links if l]))
    resume_lines.append("\n---\n")
    
    # 2. Summary
    if profile.get('professional_summary'):
        resume_lines.append("### PROFESSIONAL SUMMARY")
        for bullet in _load_json(profile['professional_summary']):
            resume_lines.append(f"- {bullet}")
        resume_lines.append("\n")
        
    # 3. Skills
    if profile.get('skills'):
        resume_lines.append("### TECHNICAL SKILLS")
        for s in profile['skills']:
            skill_list = _load_json(s['skills_list'])
            resume_lines.append(f"**{s['category']}:** {', '.join(skill_list)}")
        resume_lines.append("\n")
        
    # 4. Experience
    if profile.get('experience'):
        resume_lines.append("### PROFESSIONAL EXPERIENCE")
        for e in profile['experience']:
            end_date = e['end_date'] if e['end_date'] else 'Present'
            resume_lines.append(f"**{e['role_title']}** | {e['company_name']} | *{e['start_date']} to {end_date}*")
            for b in _load_json(e.get('role_and_contributions')):
                resume_lines.append(f"- {b}")
            resume_lines.append("\n")
            
    # 5. Education
    if profile.get('education'):
        resume_lines.append("### EDUCATION")
        for ed in profile['education']:
            resume_lines.append(f"**{ed['degree']} in {ed['field_of_study']}** | {ed['institution']}, {ed['location']} | *{ed['start_year']} - {ed['end_year']}*")
            
        resume_lines.append("\n")
            
    # 6. Projects
    if profile.get('projects'):
        resume_lines.append("### PROJECTS")
        for p in profile['projects']:
            end_date = p.get('end_date') or 'Present'
            date_str = f"*{p['start_date']} to {end_date}*" if p.get('start_date') else ""
            
            title_line = f"**{p['project_name']}**"
            if date_str: title_line += f" | {date_str}"
            if p.get('project_url'): title_line += f" | [View Project]({p['project_url']})"
            resume_lines.append(title_line)
            
            if p.get('description'):
                resume_lines.append(p['description'])
            tech = _load_json(p.get('technologies_utilized'))
            if tech:
                resume_lines.append(f"**Technologies:** {', '.join(tech)}")
            resume_lines.append("\n")

    # 7. Certifications
    if profile.get('certifications'):
        resume_lines.append("### CERTIFICATIONS")
        for c in profile['certifications']:
            org = f" | {c['issuing_organization']}" if c.get('issuing_organization') else ""
            date_str = f" | Issued: {c['issue_date']}" if c.get('issue_date') else ""
            link = f" | [Credential]({c['credential_url']})" if c.get('credential_url') else ""
            resume_lines.append(f"**{c['certificate_name']}**{org}{date_str}{link}")

    return "\n".join(resume_lines)