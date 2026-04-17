import os
import glob

files = glob.glob('Agentic_Tasks/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    # Standard check=False replacements
    if "encoding='utf-8', check=False)" in content:
        content = content.replace("encoding='utf-8', check=False)", "encoding='utf-8', check=False, timeout=120)")
        modified = True
    if "encoding='utf-8',\n                check=False\n            )" in content:
        content = content.replace("encoding='utf-8',\n                check=False\n            )", "encoding='utf-8',\n                check=False,\n                timeout=120\n            )")
        modified = True
    if "encoding='utf-8',\n                check=False)" in content:
        content = content.replace("encoding='utf-8',\n                check=False)", "encoding='utf-8',\n                check=False,\n                timeout=120)")
        modified = True
        
    # Same for check=True replacements (if any)
    if "encoding='utf-8', check=True)" in content:
        content = content.replace("encoding='utf-8', check=True)", "encoding='utf-8', check=True, timeout=120)")
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated timeouts in {filepath}")

