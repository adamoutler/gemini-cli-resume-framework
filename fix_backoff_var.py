import os
import glob

files = glob.glob('Agentic_Tasks/Orchestrator/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    # Find the line inside the try block
    if 'backoff_times = [20, 60, 180, 600]' in content:
        # Some files might have it twice or only once.
        # Just replace it with empty string where it is deeply indented, and add it right before the for loop.
        # Actually, since it's just Python, I can declare it right before `for attempt in range(MAX_RETRIES):`
        content = content.replace('for attempt in range(MAX_RETRIES):', 'backoff_times = [20, 60, 180, 600]\n    for attempt in range(MAX_RETRIES):')
        # And remove the inner ones
        content = content.replace('                backoff_times = [20, 60, 180, 600]\n', '')
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

