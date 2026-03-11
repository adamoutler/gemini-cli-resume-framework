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
MODEL = "gemini-2.0-flash"
GEMINI_TMP_DIR = os.path.expanduser("~/.gemini/tmp")

def log(message):
    print(f"[SESSION_MANAGER] {message}", flush=True)

def find_session_file_by_id(session_id):
    """Searches for the session JSON file by ID in likely locations."""
    prefix = session_id[:8]
    filename_pattern = f"*{prefix}*.json"
    
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
    
    cmd = ["gemini", "--model", model, "--output-format", "text"]
    
    try:
        # Run the init command
        subprocess.run(cmd, input=init_prompt, capture_output=True, text=True, encoding='utf-8', check=False)
        
        # Find the latest session ID
        list_cmd = "gemini --list-sessions"
        result = subprocess.check_output(list_cmd, shell=True, text=True).strip()
        
        # Parse output to find the most recent session
        lines = result.split('\n')
        if not lines: return None
        
        for line in reversed(lines):
             match = re.search(r'([a-f0-9\-]{36})', line)
             if match:
                 master_id = match.group(1)
                 log(f"{model} Master Session Created")
                 return master_id
        
        log(f"Failed to extract Session ID. Raw result: '{result}'")
        return None
            
    except Exception as e:
        log(f"Session initialization failed: {e}")
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
    dst_filename = f"session-{timestamp}-{dst_prefix}.json"
    dst_file = os.path.join(session_dir, dst_filename)
    
    try:
        with open(src_file, 'r') as f:
            data = json.load(f)
        
        # Update Session ID and Timestamp
        data['sessionId'] = worker_id
        data['lastUpdated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        with open(dst_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return worker_id
    except Exception as e:
        log(f"Error forking session: {e}")
        return None
