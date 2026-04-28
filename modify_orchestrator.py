import re
import sys

file_path = "Agentic_Tasks/Orchestrator/resume_orchestrator.py"
with open(file_path, "r") as f:
    content = f.read()

# 1. Modify def run_workflow
content = content.replace(
    "def run_workflow(jd_name, sentinel_only=False, skip_existing=False, notes=None):",
    "def run_workflow(jd_name, sentinel_only=False, skip_existing=False, notes=None, resume_from_audit=False):"
)

# 2. Add argument parsing
content = content.replace(
    "parser.add_argument(\"--notes\", help=\"Strategic notes or guidance for the builder persona (e.g., 'Lean into embedded security')\")\n    args = parser.parse_args()",
    "parser.add_argument(\"--notes\", help=\"Strategic notes or guidance for the builder persona (e.g., 'Lean into embedded security')\")\n    parser.add_argument(\"--resume-from-audit\", action=\"store_true\", help=\"Resume from the audit phase using an existing JSON draft\")\n    args = parser.parse_args()"
)
content = content.replace(
    "run_workflow(args.jd, sentinel_only=args.sentinel_only, skip_existing=args.skip_existing, notes=args.notes)",
    "run_workflow(args.jd, sentinel_only=args.sentinel_only, skip_existing=args.skip_existing, notes=args.notes, resume_from_audit=args.resume_from_audit)"
)

# 3. Handle Phase 1 and 2 wrapping and indentation
phase1_marker = "    # =========================================================================\n    # PHASE 1: SENTINEL (Trap Detection)"
phase3_marker = "    # =========================================================================\n    # PHASE 3: REFINE LOOP (Audit -> Fix -> Review -> Fix)"

if phase1_marker not in content or phase3_marker not in content:
    print("Markers not found!")
    sys.exit(1)

parts = content.split(phase3_marker)
if len(parts) != 2:
    print("Phase 3 marker found multiple times or not found.")
    sys.exit(1)

before_phase3 = parts[0]
after_phase3 = parts[1]

sub_parts = before_phase3.split(phase1_marker)
if len(sub_parts) != 2:
    print("Phase 1 marker found multiple times or not found.")
    sys.exit(1)

before_phase1 = sub_parts[0]
phase1_and_2 = phase1_marker + sub_parts[1]

# Indent Phase 1 and 2
indented_phase1_2 = "\n".join("    " + line if line.strip() else line for line in phase1_and_2.split("\n"))

# The injection block
injection = """    resume_json = None
    if resume_from_audit and os.path.exists(draft_path):
        log("SETUP", f"Resuming from existing draft: {draft_path}")
        with open(draft_path, 'r') as f:
            resume_json = json.load(f)
        log("PHASE 2/5", "Skipping Initial Build (Resuming from existing JSON)...")
    else:
"""

new_content = before_phase1 + injection + indented_phase1_2 + phase3_marker + after_phase3

with open(file_path, "w") as f:
    f.write(new_content)

print("Modifications applied successfully.")
