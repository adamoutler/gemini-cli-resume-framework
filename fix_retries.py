import os
import glob

# Files to update
files = glob.glob('Agentic_Tasks/Orchestrator/**/*.py', recursive=True)

backoff_schedule = "[20, 60, 180, 600, 600, 600]"
failure_msg = 'log("FATAL", "Failed to communicate cannot reach server. exceeded 429 threshold. Do not attempt to repeat. Do not continue working on this resume. The artifacts from this run should be considered corrupt and unusable.")\n    import sys\n    sys.exit(1)'

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # If the file contains the old retry logic, we can try to replace it.
    if 'wait_time = (2 ** attempt) * 32' in content:
        print(f"Updating {filepath}")
        content = content.replace('MAX_RETRIES = 5', 'MAX_RETRIES = 7')
        
        # Replace the wait_time line with array access
        new_wait_time = f"""
                backoff_times = {backoff_schedule}
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
        """
        content = content.replace('wait_time = (2 ** attempt) * 32', new_wait_time.strip())
        
        # Replace the final fatal log
        content = content.replace('log("FATAL", "Max retries exceeded for Gemini API call.")\n    return None', failure_msg)
        
        with open(filepath, 'w') as f:
            f.write(content)

