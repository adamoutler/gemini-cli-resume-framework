import os
import glob

files = glob.glob('Agentic_Tasks/Orchestrator/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    if 'MAX_RETRIES = 7' in content:
        content = content.replace('MAX_RETRIES = 7', 'MAX_RETRIES = 5')
        modified = True

    # Fix backoff times array
    if '[20, 60, 180, 600, 600, 600]' in content:
        content = content.replace('[20, 60, 180, 600, 600, 600]', '[20, 60, 180, 600]')
        modified = True

    # Avoid sleeping on the last attempt
    old_wait_logic = 'wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600'
    new_wait_logic = '''if attempt == MAX_RETRIES - 1:
                    break # Exit loop immediately on final failure
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600'''
    
    if old_wait_logic in content:
        content = content.replace(old_wait_logic, new_wait_logic)
        modified = True

    # Same for another potential indentation variation
    old_wait_logic_2 = 'wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600 '
    new_wait_logic_2 = '''if attempt == MAX_RETRIES - 1:
                    break
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600 '''
    if old_wait_logic_2 in content:
        content = content.replace(old_wait_logic_2, new_wait_logic_2)
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

