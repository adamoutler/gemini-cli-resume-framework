import json
import copy

input_path = "cv-data/resumes/q6-fraud-analyst-resume.json"
output_path = "cv-data/resumes/long_test_resume.json"

with open(input_path, "r") as f:
    resume = json.load(f)

# Inflate work experience (duplicate 5 times)
if "work" in resume:
    resume["work"] = resume["work"] * 5

# Add dummy sections for removal
resume["interests"] = [{"name": "Skydiving", "keywords": ["Freefall"]}] * 5
resume["languages"] = [{"language": "Spanish", "fluency": "Native"}] * 5
resume["publications"] = [{"name": "Book Title", "publisher": "Publisher", "releaseDate": "2020-01-01"}] * 5
resume["volunteer"] = [{"organization": "Red Cross", "position": "Volunteer", "startDate": "2010-01-01"}] * 5
resume["education"] = [{"institution": "Harvard", "area": "CS", "studyType": "BS"}] * 5
resume["awards"] = [{"title": "Best Award", "date": "2021-01-01", "awarder": "Awarder"}] * 5

with open(output_path, "w") as f:
    json.dump(resume, f, indent=2)

print(f"Created inflated resume at {output_path}")
