
import subprocess
import os
import shutil
import json

SESSION_DIR = "test_sessions"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

MASTER_SESSION = os.path.join(SESSION_DIR, "master.json")
WORKER_SESSION = os.path.join(SESSION_DIR, "worker.json")

# 1. Initialize Master Session
print("Initializing Master Session...")
initial_context = "The secret code is 12345. Remember this."
cmd_init = ["gemini", "--session", MASTER_SESSION]
# We pass context via stdin. If the CLI behaves like a REPL, this might be tricky.
# Usually 'gemini' CLI takes prompt as arg or stdin. 
# Let's try passing it as stdin.
proc = subprocess.run(cmd_init, input=initial_context, text=True, capture_output=True)
print(f"Init Output: {proc.stdout}")
print(f"Init Error: {proc.stderr}")

# 2. Check if file exists
if os.path.exists(MASTER_SESSION):
    print(f"Master session created: {MASTER_SESSION}")
else:
    print("Failed to create master session file.")
    # Fallback assumption: The tool might store sessions in a specific ~/.gemini dir
    # The user's script used "$HOME/.gemini/sessions/doc_master.json"
    # So the argument to --session might be a name, not a path?
    # User script: MASTER="$HOME/.gemini/sessions/doc_master.json"
    # gemini --session query_run 
    # It seems 'query_run' is the session name.
    pass

# 3. Clone and Query
print("Cloning session...")
# If the CLI stores sessions in a default dir, we need to know where.
# But if we provide a path, it might work. 
# Let's assume for now we can just copy the file if it exists.

if os.path.exists(MASTER_SESSION):
    shutil.copy(MASTER_SESSION, WORKER_SESSION)
    
    print("Querying Worker Session...")
    query = "What is the secret code?"
    # We use the copied session file
    cmd_query = ["gemini", "--session", WORKER_SESSION, "--output-format", "text"]
    proc_q = subprocess.run(cmd_query, input=query, text=True, capture_output=True)
    print(f"Query Output: {proc_q.stdout}")
else:
    print("Skipping query test due to missing master session.")
