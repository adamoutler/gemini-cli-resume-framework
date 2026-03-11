import os
import json
import re

CV_DATA_DIR = "cv-data"

# Mapping rules based on directory
RULES = {
    "news-media-mentions": {
        "document_type": "Media Mention",
        "domain": "External Recognition"
    },
    "authored-articles": {
        "document_type": "Article",
        "domain": "Technical Writing"
    },
    "personal-projects": {
        "document_type": "Project Review",
        "domain": "Software Engineering"
    },
    "general": {
         # General is tricky, usually manual, but we can set defaults if missing
         "document_type": "Reference Data",
         "domain": "Professional Profile"
    }
}

def fix_file(file_path, rules):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract FrontMatter
    match = re.search(r'^---\s*\n({.*?})\n---\s*\n', content, re.DOTALL | re.MULTILINE)
    
    if not match:
        print(f"Skipping {file_path}: No valid FrontMatter found.")
        return False

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Skipping {file_path}: Invalid JSON.")
        return False

    modified = False

    # Apply Rules
    if "document_type" not in data:
        data["document_type"] = rules["document_type"]
        modified = True
    
    if "domain" not in data:
        data["domain"] = rules["domain"]
        modified = True
        
    if "keywords" not in data:
        data["keywords"] = [] # Initialize empty list, better than missing
        modified = True

    if modified:
        # Reconstruct file
        new_json_str = json.dumps(data, indent=2)
        # Regex replace the JSON block
        # Use lambda to avoid bad escape errors in repl string
        new_content = re.sub(
            r'^---\s*\n{.*?}\n---\s*\n', 
            lambda m: f"---\n{new_json_str}\n---\n", 
            content, 
            flags=re.DOTALL | re.MULTILINE, 
            count=1
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {file_path}")
        return True
    
    return False

def main():
    print("Starting Metadata Bulk Fix...")
    count = 0
    for category, rules in RULES.items():
        dir_path = os.path.join(CV_DATA_DIR, category)
        if not os.path.exists(dir_path):
            continue
            
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".md"):
                    if fix_file(os.path.join(root, file), rules):
                        count += 1
    
    print(f"Done. Updated {count} files.")

if __name__ == "__main__":
    main()
