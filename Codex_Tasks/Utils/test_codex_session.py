
import subprocess
import os
import shutil
import json

# 1. Initialize Master Session
print("Initializing Master Session...")
initial_context = "The secret code is 12345. Remember this."
cmd_init = ["codex", "exec", "--model", "gpt-5.4-mini", "--color", "never", "-"]
proc = subprocess.run(cmd_init, input=initial_context, text=True, capture_output=True)
print(f"Init Output: {proc.stdout}")
print(f"Init Error: {proc.stderr}")

print("Codex exec completed. Inspect ~/.codex/sessions for the persisted session JSONL.")
