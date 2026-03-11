import shutil
import subprocess
import sys
import os

def check_binary(binary_name, args=["--version"]):
    """Checks if a binary exists and can be executed."""
    path = shutil.which(binary_name)
    if not path:
        return False, None
    
    try:
        # Run with a small timeout to avoid hanging
        result = subprocess.run([binary_name] + args, capture_output=True, text=True, timeout=5)
        return True, path
    except Exception as e:
        return False, str(e)

def main():
    print("Checking system dependencies...", flush=True)
    
    # List of binaries and the command to verify them
    dependencies = [
        ("gemini", ["--version"]),
        ("pandoc", ["--version"]),
        ("xelatex", ["--version"]),
        ("node", ["--version"]),
        ("resume", ["--version"]),
        ("pdfinfo", ["-v"]),
        ("pdftotext", ["-v"]),
        ("git", ["--version"]),
        ("curl", ["--version"]),
        ("jq", ["--version"])
    ]
    
    failed = []
    for binary, args in dependencies:
        success, info = check_binary(binary, args)
        if success:
            print(f"[OK] {binary} found at {info}", flush=True)
        else:
            print(f"[ERROR] {binary} is missing or broken: {info}", flush=True)
            failed.append(binary)
            
    if failed:
        print(f"\n[FATAL] Missing or broken dependencies: {', '.join(failed)}", flush=True)
        print("Please install required system packages and try again.", flush=True)
        sys.exit(1)
    
    print("All dependencies satisfied.\n", flush=True)

if __name__ == "__main__":
    main()
