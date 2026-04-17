import os

filepath = 'Agentic_Tasks/Orchestrator/utils/session_manager.py'

with open(filepath, 'r') as f:
    content = f.read()

old_block = """    try:
        # Run the init command
        result = subprocess.run(cmd, input=init_prompt, capture_output=True, text=True, encoding='utf-8', check=False)
        
        if result.returncode != 0:
            log(f"Master session initialization failed with exit code {result.returncode}. Error: {result.stderr}")
            return None"""

new_block = """    backoff_times = [20, 60, 180, 600, 600, 600]
    MAX_RETRIES = 7
    result = None
    for attempt in range(MAX_RETRIES):
        try:
            # Run the init command
            result = subprocess.run(cmd, input=init_prompt, capture_output=True, text=True, encoding='utf-8', check=False)
            
            if result.returncode != 0:
                err_msg = result.stderr.lower() if result.stderr else ""
                if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg:
                    wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
                    log(f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s... Error: {err_msg[:100]}")
                    time.sleep(wait_time)
                    continue
                else:
                    log(f"Master session initialization failed with exit code {result.returncode}. Error: {result.stderr}")
                    return None
            else:
                break # Success
        except Exception as e:
            log(f"Session initialization failed: {e}")
            return None
    else:
        log("Failed to communicate cannot reach server. exceeded 429 threshold. Do not attempt to repeat. Do not continue working on this resume. The artifacts from this run should be considered corrupt and unusable.")
        import sys
        sys.exit(1)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Successfully patched utils/session_manager.py")
else:
    print("Could not find old block in utils/session_manager.py")
