import os
import re

def generate_dynamic_mock():
    """Generates a JSON mock based on active Handlebars partials."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    theme_dir = os.path.join(project_root, "custom-resume-theme")
    main_hbs = os.path.join(theme_dir, "resume.hbs")
    
    if not os.path.exists(main_hbs):
        return "{}"

    with open(main_hbs, 'r') as f:
        content = f.read()

    # Find active partials
    partials = re.findall(r"\{\{>\s*([a-zA-Z0-9_]+)\s*\}\}", content)
    
    mock = [
        "{",
        '  "basics": {',
        '    "name": "Full Name",',
        '    "label": "Target Title",',
        '    "email": "user@example.com",',
        '    "phone": "555-555-5555",',
        '    "url": "https://adamoutler.com",',
        '    "summary": "High-impact snapshot...",',
        '    "location": {',
        '      "address": "123 Main St",',
        '      "postalCode": "12345",',
        '      "city": "City",',
        '      "region": "State",',
        '      "countryCode": "US"',
        '    },',
        '    "profiles": [',
        '      {',
        '        "network": "LinkedIn",',
        '        "username": "https://linkedin.com/in/user",',
        '        "url": "https://linkedin.com/in/user"',
        '      }',
        '    ]',
        '  },'
    ]

    if "career_highlights" in partials:
        mock.extend([
            '  "careerHighlights": [',
            '    "Quantitative highlight 1",',
            '    "Quantitative highlight 2"',
            '  ],'
        ])
        
    if "work" in partials:
        mock.extend([
            '  "work": [',
            '    {',
            '      "name": "Company Name",',
            '      "company": "Company Name",',
            '      "position": "Job Title",',
            '      "startDate": "YYYY-MM-DD",',
            '      "endDate": "YYYY-MM-DD",',
            '      "summary": "Role overview...",',
            '      "highlights": ["Impact 1", "Impact 2"]',
            '    }',
            '  ],'
        ])
        
    if "education" in partials:
        mock.extend([
            '  "education": [',
            '    {',
            '      "institution": "University Name",',
            '      "area": "Degree Area",',
            '      "studyType": "Bachelor",',
            '      "startDate": "YYYY-MM-DD",',
            '      "endDate": "YYYY-MM-DD",',
            '      "score": "GPA"',
            '    }',
            '  ],'
        ])

    if "certificates" in partials:
        mock.extend([
            '  "certificates": [',
            '    {',
            '      "name": "Cert Name",',
            '      "date": "YYYY-MM-DD",',
            '      "issuer": "Issuer",',
            '      "url": "https://cert.com"',
            '    }',
            '  ],'
        ])
        
    if "awards" in partials:
        mock.extend([
            '  "awards": [',
            '    {',
            '      "title": "Award Name",',
            '      "date": "YYYY-MM-DD",',
            '      "awarder": "Awarder",',
            '      "summary": "Details"',
            '    }',
            '  ],'
        ])

    if "projects" in partials:
        mock.extend([
            '  "projects": [',
            '    {',
            '      "name": "Project Name",',
            '      "position": "Project Name",',
            '      "startDate": "YYYY-MM-DD",',
            '      "endDate": "YYYY-MM-DD",',
            '      "url": "https://github.com/...",',
            '      "summary": "Overview",',
            '      "highlights": ["Detail 1"]',
            '    }',
            '  ],'
        ])

    if "volunteer" in partials:
        mock.extend([
            '  "volunteer": [',
            '    {',
            '      "organization": "Org Name",',
            '      "position": "Role",',
            '      "startDate": "YYYY-MM-DD",',
            '      "endDate": "YYYY-MM-DD",',
            '      "summary": "Overview",',
            '      "highlights": ["Detail 1"]',
            '    }',
            '  ],'
        ])

    if "languages" in partials:
        mock.extend([
            '  "languages": [',
            '    {',
            '      "language": "English",',
            '      "fluency": "Native speaker"',
            '    }',
            '  ],'
        ])

    if "skills" in partials:
        mock.extend([
            '  "skills": [',
            '    {',
            '      "name": "Category (e.g. Cloud)",',
            '      "level": "master",',
            '      "keywords": ["AWS", "GCP"]',
            '    }',
            '  ]'
        ])

    # Remove the trailing comma from the last item
    if mock[-1].endswith(","):
         mock[-1] = mock[-1][:-1]

    mock.append("}")
    
    return "\n".join(mock)

if __name__ == "__main__":
    print(generate_dynamic_mock())