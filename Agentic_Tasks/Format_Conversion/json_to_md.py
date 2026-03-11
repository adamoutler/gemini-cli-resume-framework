import json
import sys
import os

def json_to_markdown(json_path, output_path):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(json_path, 'r') as f:
        data = json.load(f)

    basics = data.get('basics', {})
    work = data.get('work', [])
    education = data.get('education', [])
    skills = data.get('skills', [])
    projects = data.get('projects', [])

    md = []

    # Helper for ATS-compliant date formatting (MM/YYYY)
    def format_date(date_str):
        if not date_str: return ""
        if date_str.lower() in ["present", "current"]: return "Present"
        try:
            # Handle YYYY-MM-DD or YYYY-MM
            parts = date_str.split('-')
            if len(parts) >= 2:
                return f"{parts[1]}/{parts[0]}" # Return MM/YYYY
            return date_str # Fallback
        except:
            return date_str

    # Header
    md.append(f"# {basics.get('name', '')}")
    
    # Contact Info: Email | Phone | Location
    contact_parts = []
    if basics.get('email'): contact_parts.append(basics.get('email'))
    if basics.get('phone'): contact_parts.append(basics.get('phone'))
    
    # Location (City, Region) - Critical for ATS
    location = basics.get('location', {})
    loc_str = []
    if location.get('city'): loc_str.append(location.get('city'))
    if location.get('region'): loc_str.append(location.get('region'))
    if loc_str: contact_parts.append(", ".join(loc_str))
    
    md.append(" | ".join(contact_parts))
    
    profile_links = []
    for profile in basics.get('profiles', []):
        network = profile.get('network', '')
        url = profile.get('url', '')
        if network and url:
            # ATS Tip: Ensure URL is visible or clearly labeled. 
            # Markdown link is okay, but plain text is safer for some parsers.
            profile_links.append(f"[{network}]({url})")
    if profile_links:
        md.append(f" | {' | '.join(profile_links)}")
    md.append("\n")

    # ATS Optimization: Use "Personal Website" instead of "AI Persona" and ensure raw URL is visible or standard text link.
    if basics.get('url'):
        md.append(f"[Personal Website]({basics.get('url', '')})\n")

    # Summary
    md.append("## Professional Summary\n")
    md.append(f"**{basics.get('label', '')}**")
    md.append(f"{basics.get('summary', '')}\n")

    # Skills
    md.append("## Core Competencies\n")
    for skill in skills:
        md.append(f"*   **{skill.get('name', '')}:** {', '.join(skill.get('keywords', []))}.")
    md.append("\n")

    # Experience
    md.append("## Professional Experience\n")
    for job in work:
        start = format_date(job.get('startDate', ''))
        end = format_date(job.get('endDate', 'Present'))
        
        # ATS Requirement: Company Name MUST appear before Position Title
        md.append(f"### {job.get('name', '')} | {job.get('position', '')}")
        md.append(f"**{start} – {end}**")
        
        # Location in Experience if available
        if job.get('location'):
             md.append(f"*{job.get('location')}*")
             
        md.append(f"*{job.get('summary', '')}*\n")
        for highlight in job.get('highlights', []):
            md.append(f"*   {highlight}")
        md.append("\n")

    # Projects
    md.append("## Selected Technical Projects\n")
    for proj in projects:
        md.append(f"*   **{proj.get('name', '')}:** {proj.get('summary', '')}")
        for highlight in proj.get('highlights', []):
            md.append(f"    *   {highlight}")
        md.append("\n")

    # Education
    md.append("## Education\n")
    for edu in education:
        md.append(f"*   **{edu.get('institution', '')}:** {edu.get('area', '')} ({edu.get('studyType', '')}). {edu.get('summary', '')}")

    # Volunteer
    if data.get('volunteer'):
        md.append("## Volunteer Work\n")
        for vol in data.get('volunteer', []):
            start = vol.get('startDate', '')[:4]
            end = vol.get('endDate', 'Present')[:4]
            md.append(f"*   **{vol.get('organization', '')}** | {vol.get('position', '')} ({start} – {end})")
            md.append(f"    *   {vol.get('summary', '')}")
        md.append("\n")

    # Awards & Patents
    if data.get('awards'):
        md.append("## Awards & Patents\n")
        for award in data.get('awards', []):
            date = award.get('date', '')[:4]
            md.append(f"*   **{award.get('title', '')}** ({award.get('awarder', '')}, {date})")
            md.append(f"    *   {award.get('summary', '')}")
        md.append("\n")

    # Certificates
    if data.get('certificates'):
        md.append("## Certifications\n")
        for cert in data.get('certificates', []):
            md.append(f"*   **{cert.get('name', '')}** ({cert.get('issuer', '')})")
        md.append("\n")

    # Languages
    if data.get('languages'):
        md.append("## Languages\n")
        langs = [f"{lang.get('language', '')} ({lang.get('fluency', '')})" for lang in data.get('languages', [])]
        md.append(", ".join(langs))
        md.append("\n")

    with open(output_path, 'w') as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json_to_md.py <input_json_path> <output_md_path>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    json_to_markdown(json_path, output_path)
