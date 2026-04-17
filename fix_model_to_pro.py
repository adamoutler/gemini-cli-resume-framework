import os
import glob

files = glob.glob('Agentic_Tasks/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    if 'gemini-3.1-flash-preview' in content:
        content = content.replace('gemini-3.1-flash-preview', 'gemini-3.1-pro-preview')
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath} to pro")

