import json
import re

def remove_markdown_from_json(data):
    if isinstance(data, dict):
        return {k: remove_markdown_from_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_markdown_from_json(elem) for elem in data]
    elif isinstance(data, str):
        # Remove bold markdown (**text**)
        data = re.sub(r'\*\*(.*?)\*\*', r'\1', data)
        # Remove single asterisk markdown (*text*) - though not used in original
        data = re.sub(r'\*(.*?)\*', r'\1', data)
        return data
    else:
        return data

file_path = 'cv-data/resumes/Sonatus_Senior_Director_DevOps_Resume.json'
with open(file_path, 'r') as f:
    resume_data = json.load(f)

cleaned_resume_data = remove_markdown_from_json(resume_data)

with open(file_path, 'w') as f:
    json.dump(cleaned_resume_data, f, indent=2)

print(f"Removed Markdown formatting from {file_path}")
