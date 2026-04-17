import glob

files = glob.glob('Agentic_Tasks/**/*.py', recursive=True)
files_to_fix = [
    'Agentic_Tasks/Orchestrator/resume_orchestrator.py',
    'Agentic_Tasks/Resume_Audit/audit_content_new.py',
    'Agentic_Tasks/Orchestrator/utils/gemini_client.py',
    'Agentic_Tasks/Orchestrator/generate_cover_letter_only.py',
    'Agentic_Tasks/Orchestrator/utils/session_manager.py'
]

for filepath in files_to_fix:
    with open(filepath, 'r') as f:
        content = f.read()

    # Move `import time` to the top if not present globally
    if 'import time' not in content[:500]:
        content = "import time\n" + content
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Added import time to {filepath}")
    else:
        # Check if we accidentally put it in the local block but not globally
        lines = content.split('\n')
        has_global_time = any(line.startswith('import time') for line in lines[:20])
        if not has_global_time:
            content = "import time\n" + content
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Added global import time to {filepath}")

