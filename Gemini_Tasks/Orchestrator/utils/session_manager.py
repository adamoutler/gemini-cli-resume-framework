import os
import json
import time
import subprocess
import re
import uuid
import glob
import sys

# Configuration
# We use the same model defined in the orchestrator, or default to flash for speed/cost if unspecified
MODEL = "gemini-2.5-flash-lite"
GEMINI_TMP_DIR = os.path.expanduser("~/.gemini/tmp")

def log(message):
    print(f"[SESSION_MANAGER] {message}", flush=True)

def find_session_file_by_id(session_id):
    """Searches for the session JSON file by ID in likely locations."""
    prefix = session_id[:8]
    filename_pattern = f"*{prefix}*.json*"
    
    search_paths = []
    
    # 1. Check GEMINI_PROJECT_TMP_DIR if set
    env_dir = os.environ.get('GEMINI_PROJECT_TMP_DIR')
    if env_dir:
        search_paths.append(env_dir)
        search_paths.append(os.path.join(env_dir, "chats"))
        
    # 2. Check standard location ~/.gemini/tmp
    if os.path.exists(GEMINI_TMP_DIR):
        search_paths.extend(glob.glob(os.path.join(GEMINI_TMP_DIR, "*", "chats")))
        search_paths.append(GEMINI_TMP_DIR)

    for path in search_paths:
        if not path or not os.path.exists(path): continue
        
        full_path = os.path.join(path, filename_pattern)
        matches = glob.glob(full_path)
        if matches:
            return matches[0]
            
    return None

def init_master_session(cv_context, jd_text, model=MODEL):
    """Initializes a master session with CV Data and JD, returning the Session ID."""
    log(f"Initializing Master Session with {model} (Time-to-First-Token Optimization)...")
    
    init_prompt = (
        "# MISSION INITIALIZATION\n"
        "You are the central 'Resume Generation Engine'. I am loading your working memory with the source of truth.\n\n"
        "## SOURCE DOCUMENT: CV DATA\n"
        "```text\n"
        f"{cv_context}\n"
        "```\n\n"
        "## SOURCE DOCUMENT: TARGET JOB DESCRIPTION\n"
        "```text\n"
        f"{jd_text}\n"
        "```\n\n"
        "## SYSTEM INSTRUCTION\n"
        "1. Ingest the documents above.\n"
        "2. Do not output any content yet.\n"
        "3. Reply only with: 'ACK'."
    )
    
    cmd = ["gemini", "-e", "", "--model", model, "-p", "reply with OK", "--output-format", "text"]
    
    backoff_times = [20, 60, 180, 600]
    MAX_RETRIES = 5
    result = None
    backoff_times = [20, 60, 180, 600]
    for attempt in range(MAX_RETRIES):
        try:
            # Run the init command
            result = subprocess.run(cmd, input=init_prompt, capture_output=True, text=True, encoding='utf-8', check=False, timeout=1800)
            
            if result.returncode != 0:
                err_msg = result.stderr.lower() if result.stderr else ""
                if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg:
                    if attempt == MAX_RETRIES - 1:
                        break
                    wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
                    log(f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s... Error: {err_msg[:100]}")
                    time.sleep(wait_time)
                    continue
                else:
                    log(f"Master session initialization failed with exit code {result.returncode}. Error: {result.stderr}")
                    return None
            else:
                break # Success
        except subprocess.TimeoutExpired:
            log(f"Gemini API Timeout (Attempt {attempt+1}/{MAX_RETRIES}). Backing off...")
            time.sleep(backoff_times[attempt] if attempt < len(backoff_times) else 600)
            continue
        except Exception as e:
            log(f"Session initialization failed: {e}")
            return None
    else:
        log("Failed to communicate cannot reach server. exceeded 429 threshold. Do not attempt to repeat. Do not continue working on this resume. The artifacts from this run should be considered corrupt and unusable.")
        import sys
        sys.exit(1)
        
    try:
        # Find the latest session ID
        list_cmd = "gemini --list-sessions"
        result_list = subprocess.check_output(list_cmd, shell=True, text=True).strip()
        
        # Parse output to find the most recent session
        lines = result_list.split('\n')
        if not lines: return None
        
        for line in reversed(lines):
             match = re.search(r'([a-f0-9\-]{36})', line)
             if match:
                 master_id = match.group(1)
                 # Verify the session actually exists on disk before returning it
                 if find_session_file_by_id(master_id):
                     log(f"{model} Master Session Created: {master_id}")
                     return master_id
                 else:
                     log(f"Master session ID {master_id} found in list, but file is missing on disk.")
                     return None
        
        log(f"Failed to extract Session ID. Raw result: '{result_list}'")
        return None
            
    except Exception as e:
        log(f"Session listing failed: {e}")
        return None

def fork_session(master_id):
    """Creates a lightweight copy of the master session for a specific task."""
    src_file = find_session_file_by_id(master_id)
    
    if not src_file:
        log(f"FATAL: Master session file not found for {master_id}")
        return None
        
    session_dir = os.path.dirname(src_file)
    worker_id = str(uuid.uuid4())
    
    timestamp = time.strftime("%Y-%m-%dT%H-%M")
    dst_prefix = worker_id[:8]
    ext = '.jsonl' if src_file.endswith('.jsonl') else '.json'
    dst_filename = f"session-{timestamp}-{dst_prefix}{ext}"
    dst_file = os.path.join(session_dir, dst_filename)
    
    try:
        lines = []
        with open(src_file, 'r') as f:
            for line in f:
                if line.strip():
                    lines.append(json.loads(line))
        
        # If it's a single dictionary (old format) or list of dicts (jsonl)
        if isinstance(lines[0], dict) and 'sessionId' in lines[0]:
            lines[0]['sessionId'] = worker_id
            lines[0]['lastUpdated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            with open(dst_file, 'w') as f:
                if src_file.endswith('.jsonl'):
                    for obj in lines:
                        f.write(json.dumps(obj) + '\n')
                else:
                    json.dump(lines[0], f, indent=2)
            return worker_id
        else:
            log("Unrecognized session file format.")
            return None
            
    except Exception as e:
        log(f"Error forking session: {e}")
        return None
