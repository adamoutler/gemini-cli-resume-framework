import os
import glob

files = glob.glob('Agentic_Tasks/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    if 'time.sleep(6)' in content:
        content = content.replace('time.sleep(6)', 'time.sleep(10)')
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

