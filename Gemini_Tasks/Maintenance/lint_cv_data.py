import os
import json
import re
import sys

# Configuration
CV_DATA_DIR = "cv-data"
REQUIRED_FIELDS = ["title", "summary", "keywords", "document_type", "domain"]
BANNED_WORDS = [r"\bI\b", r"\bmy\b", r"\bme\b", r"\bmine\b"] # 1st person pronouns

def parse_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Regex to find JSON FrontMatter between lines containing only ---
    # Matches:
    # ---
    # { ... }
    # ---
    match = re.search(r'^---\s*\n({.*?})\n---\s*\n', content, re.DOTALL | re.MULTILINE)
    
    if not match:
        return None, "No valid JSON FrontMatter found (must be wrapped in '---' and contain valid JSON)"
    
    try:
        data = json.loads(match.group(1))
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON syntax: {e}"

def check_banned_words(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Strip FrontMatter to only check body text
    content = re.sub(r'^---\s*\n{.*?}\n---\s*\n', '', content, flags=re.DOTALL | re.MULTILINE)
    
    issues = []
    for pattern in BANNED_WORDS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found banned word matching '{pattern}' (Voice should be 3rd person)")
    return issues

def validate_file(file_path):
    issues = []
    filename = os.path.basename(file_path)
    
    # 1. Check FrontMatter
    metadata, error = parse_frontmatter(file_path)
    if error:
        return [error] # Critical error, stop checking this file
    
    # 2. Check Required Fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            issues.append(f"Missing required field: '{field}'")
            
    # 3. Check Date Logic
    # Professional Experience needs start/end dates.
    # Other types (like articles, projects) usually need a single date.
    # 'general' category files usually don't need dates.
    if "PROFESSIONAL EXPERIENCE" in file_path:
        if "start_date" not in metadata:
             issues.append("Missing 'start_date' (Required for Professional Experience)")
        # end_date is optional (could be "Present") but usually good to have present or null
    elif not file_path.startswith(os.path.join(CV_DATA_DIR, "general")):
        if "date" not in metadata and "start_date" not in metadata:
            issues.append("Missing 'date' or 'start_date'")

    # 4. Check Voice (1st Person Check)
    # Skip checking specific files that might allow it (like 'authored-articles' if they are opinions)
    # But generally enforce 3rd person for CV data.
    # if "authored-articles" not in file_path:
    #     voice_issues = check_banned_words(file_path)
    #     issues.extend(voice_issues)

    return issues

def main():
    print(f"Linting {CV_DATA_DIR}...")
    print("-" * 60)
    
    error_count = 0
    file_count = 0
    
    for root, dirs, files in os.walk(CV_DATA_DIR):
        # Ignore the resumes directory entirely
        if "resumes" in dirs:
            dirs.remove("resumes")
            
        for file in files:
            if file.endswith(".md"):
                file_count += 1
                file_path = os.path.join(root, file)
                file_issues = validate_file(file_path)
                
                if file_issues:
                    print(f"FILE: {file_path}")
                    for issue in file_issues:
                        print(f"  [X] {issue}")
                    print("-" * 60)
                    error_count += 1

    print(f"Summary: Checked {file_count} files.")
    if error_count == 0:
        print("SUCCESS: No issues found.")
        sys.exit(0)
    else:
        print(f"FAILURE: Found issues in {error_count} files.")
        sys.exit(1)

if __name__ == "__main__":
    main()
