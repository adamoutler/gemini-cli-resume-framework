import os
import re

CV_DATA_DIR = "cv-data"

def fix_metadata_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return False

    # Regex logic:
    # 1. Look for lines starting with **Target Audience:**
    # 2. Look for lines starting with **Purpose:**
    # 3. Ensure they become bullet points if they aren't already.
    
    # We replace:
    # ^**Target Audience:** ...
    # with
    # *   **Target Audience:** ...
    #
    # But we must be careful not to double-bullet (e.g., "*   *   **Target...")
    
    new_content = content
    
    # Pattern: Start of line (multi-line mode), optional whitespace, NO bullet, then **Target Audience:**
    # We use sub to add the bullet.
    
    # Generic fix for common metadata keys at start of line
    # Keys to fix: Target Audience, Purpose, Date, Domain, Role, Tech Stack
    keys_to_fix = [
        r'\*\*Target Audience:\*\*',
        r'\*\*Purpose:\*\*',
        r'\*\*Date:\*\*',
        r'\*\*Domain:\*\*',
        r'\*\*Role:\*\*',
        r'\*\*Tech Stack:\*\*',
        r'\*\*Role & Responsibility:\*\*'
    ]
    
    for key_pattern in keys_to_fix:
        # 1. Add bullet if missing
        new_content = re.sub(
            r'^(\s*)(?!\*\s)(?!\-\s)(' + key_pattern + ')', 
            r'\1*   \2', 
            new_content, 
            flags=re.MULTILINE
        )
        
        # 2. Ensure newline before the bullet if needed (separation from headers/text)
        new_content = re.sub(
            r'([^\n])\n(\*   ' + key_pattern + ')', 
            r'\1\n\n\2', 
            new_content
        )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk(CV_DATA_DIR):
        for file in files:
            if file.endswith(".md"):
                if fix_metadata_lines(os.path.join(root, file)):
                    count += 1
    print(f"Finished. Modified {count} files.")

if __name__ == "__main__":
    main()
