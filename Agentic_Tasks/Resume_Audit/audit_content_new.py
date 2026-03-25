import json
import os
import sys
import subprocess
import glob
import time
from datetime import datetime
import math
import argparse
import hashlib
import concurrent.futures
import re
import uuid
import shutil

# Add Orchestrator to path to import utils
ORCHESTRATOR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Orchestrator")
sys.path.append(ORCHESTRATOR_DIR)
from utils.context_loader import load_persona
from utils.session_manager import fork_session # Import from shared manager

# Configuration
BATCH_SIZE = 5
MAX_WORKERS = 3  # Workers for parallel auditing
MODEL = "gemini-3-flash-preview" # Fast audit model
CV_DATA_DIR = "./cv-data"
TMP_DIR = "/tmp/gemini_cv_audit"
LOG_FILE = os.path.join(TMP_DIR, "audit_debug.log")

# Auto-set GEMINI_PROJECT_TMP_DIR if not set
if "GEMINI_PROJECT_TMP_DIR" not in os.environ:
    unique_run_id = uuid.uuid4().hex[:8]
    generated_tmp_dir = f"/tmp/gemini_audit_{unique_run_id}"
    os.environ["GEMINI_PROJECT_TMP_DIR"] = generated_tmp_dir
    os.makedirs(generated_tmp_dir, exist_ok=True)
else:
    os.makedirs(os.environ["GEMINI_PROJECT_TMP_DIR"], exist_ok=True)

def ensure_tmp_dir():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")
    except: pass

def get_checkpoint_path(resume_path):
    resume_abs_path = os.path.abspath(resume_path)
    file_hash = hashlib.md5(resume_abs_path.encode()).hexdigest()
    filename = os.path.basename(resume_path)
    return os.path.join(TMP_DIR, f"checkpoint_{filename}_{file_hash}.json")

def flatten_resume(data):
    """Flattens the resume JSON into a list of verifyable claims."""
    claims = []
    seen_hashes = set()

    def add_claim(ref, text):
        if not text: return
        unique_str = f"{ref}:{text.strip()}"
        claim_hash = hashlib.md5(unique_str.encode()).hexdigest()
        
        if claim_hash not in seen_hashes:
            claims.append({"ref": ref, "claim": text})
            seen_hashes.add(claim_hash)
    
    # Basics
    if 'basics' in data and 'summary' in data['basics']:
        add_claim("basics.summary", data['basics']['summary'])
        
    # Work Experience
    if 'work' in data:
        for i, job in enumerate(data['work']):
            company = job.get('name', 'Unknown Company')
            position = job.get('position', 'Unknown Role')
            context_str = f" [Context: {company}, {position}]"
            
            if 'position' in job: add_claim(f"work[{i}].position", f"{job['position']} (Job Title for {company})" + context_str)
            if 'startDate' in job: add_claim(f"work[{i}].startDate", f"{job['startDate']} (Start Date for {company})" + context_str)
            if 'endDate' in job: add_claim(f"work[{i}].endDate", f"{job['endDate']} (End Date for {company})" + context_str)
            if 'summary' in job: add_claim(f"work[{i}].summary", job['summary'] + context_str)
            if 'highlights' in job:
                for j, highlight in enumerate(job['highlights']):
                    add_claim(f"work[{i}].highlights[{j}]", highlight + context_str)
                    
    # Projects
    if 'projects' in data:
        for i, proj in enumerate(data['projects']):
            proj_name = proj.get('name', 'Unknown Project')
            context_str = f" [Context: Project '{proj_name}']"

            if 'startDate' in proj: add_claim(f"projects[{i}].startDate", f"{proj['startDate']} (Start Date)" + context_str)
            if 'endDate' in proj: add_claim(f"projects[{i}].endDate", f"{proj['endDate']} (End Date)" + context_str)
            if 'url' in proj: add_claim(f"projects[{i}].url", f"{proj['url']} (Project URL)" + context_str)
            if 'description' in proj: add_claim(f"projects[{i}].description", proj['description'] + context_str)
            if 'highlights' in proj:
                for j, highlight in enumerate(proj['highlights']):
                    add_claim(f"projects[{i}].highlights[{j}]", highlight)
                    
    # Education
    if 'education' in data:
        for i, edu in enumerate(data['education']):
            institution = edu.get('institution', 'Unknown School')
            claim_parts = [institution, edu.get('area'), edu.get('studyType')]
            claim_text = " - ".join(filter(None, claim_parts))
            add_claim(f"education[{i}]", claim_text)
            
            if 'startDate' in edu: add_claim(f"education[{i}].startDate", f"{edu['startDate']} (Start Date for {institution})")
            if 'endDate' in edu: add_claim(f"education[{i}].endDate", f"{edu['endDate']} (End Date for {institution})")
            if 'score' in edu: add_claim(f"education[{i}].score", f"{edu['score']} (Score/GPA for {institution})")
                
    # Volunteer
    if 'volunteer' in data:
        for i, vol in enumerate(data['volunteer']):
            if 'summary' in vol: add_claim(f"volunteer[{i}].summary", vol['summary'])
            if 'highlights' in vol:
                for j, highlight in enumerate(vol['highlights']):
                    add_claim(f"volunteer[{i}].highlights[{j}]", highlight)

    # Certificates
    if 'certificates' in data:
        for i, cert in enumerate(data['certificates']):
            claim_parts = [cert.get('name'), cert.get('issuer')]
            claim_text = " - ".join(filter(None, claim_parts))
            add_claim(f"certificates[{i}]", claim_text)

    # Awards
    if 'awards' in data:
        for i, award in enumerate(data['awards']):
            if 'title' in award: add_claim(f"awards[{i}].title", f"{award['title']} (Award Title)")
            if 'date' in award: add_claim(f"awards[{i}].date", f"{award['date']} (Award Date)")
            if 'awarder' in award: add_claim(f"awards[{i}].awarder", f"{award['awarder']} (Awarder)")
            if 'summary' in award: add_claim(f"awards[{i}].summary", award['summary'])

    # Skills
    if 'skills' in data:
        for i, skill in enumerate(data['skills']):
            category = skill.get('name', 'General')
            keywords = skill.get('keywords', [])
            if keywords:
                keywords_str = ", ".join(keywords)
                claim_text = f"Skills with Keywords: **{category}**: {keywords_str}"
                add_claim(f"skills[{i}]", claim_text)
                
    return claims

def load_context(data_dir):
    context = []
    files = glob.glob(os.path.join(data_dir, "**/*.md"), recursive=True)
    log(f"Loading context from {len(files)} files...")
    context.append("# MISSION INITIALIZATION")
    context.append("You are the Resume Generation Engine. I am loading your working memory with the source of truth.")
    context.append("\n## SOURCE DOCUMENT: CV DATA")
    context.append("```text")
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                context.append(f"\n--- FILE: {os.path.basename(filepath)} ---")
                context.append(content)
        except: pass
    context.append("\n```")
    return "\n".join(context)

def init_session(context_text):
    """Initializes a local master session if one is not provided."""
    init_prompt = f"{context_text}\n\n## SYSTEM INSTRUCTION\n1. Ingest the documents above.\n2. Do not output any content yet.\n3. Reply only with: 'ACK'." 
    
    cmd = ["gemini", "--model", MODEL, "--output-format", "text"]
    try:
        subprocess.run(cmd, input=init_prompt, capture_output=True, text=True, encoding='utf-8', check=False)
        list_cmd = "gemini --list-sessions"
        result = subprocess.check_output(list_cmd, shell=True, text=True).strip()
        
        lines = result.split('\n')
        if not lines: return None
        
        for line in reversed(lines):
             match = re.search(r'\[([a-f0-9\-]{36})\]', line)
             if match:
                 return match.group(1)
        return None
    except Exception as e:
        log(f"Session initialization failed: {e}")
        return None

def init_session_pool(context_text, count, parent_session_id=None):
    """Initializes a master session (or uses existing) then duplicates it for workers."""
    
    if parent_session_id:
        log(f"Using provided Master Session: {parent_session_id}")
        master_id = parent_session_id
    else:
        log(f"Initializing Local Master Session...")
        master_id = init_session(context_text)
    
    if not master_id:
        log("FATAL: Master session initialization failed.")
        return []
    
    log(f"Master Session Ready: {master_id}. Duplicating {count} times...")
    
    # Wait briefly for file system sync
    time.sleep(2)
    
    sessions = []
    for i in range(count):
        worker_id = str(uuid.uuid4())
        # Use the utility directly, which handles file duplication for us
        # Note: The imported function name in 'session_manager' is 'fork_session', not 'duplicate_session_json'.
        
        worker_id_result = fork_session(master_id)
        
        if worker_id_result:
            sessions.append(worker_id_result)
            log(f"  - Worker {i+1}/{count} Ready: {worker_id_result[:8]}...")
        else:
            log(f"  - Worker {i+1}/{count} Failed to duplicate.")
    
    log(f"Session Pool Ready: {len(sessions)} sessions available.")
    return sessions

MAX_RETRIES = 5

def call_agent(prompt, session_id=None):
    cmd = ["gemini", "--model", MODEL, "--output-format", "text"]
    if session_id:
        cmd.extend(["--resume", session_id])

    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding='utf-8', check=False)
            
            if result.returncode == 0:
                return result.stdout

            err_msg = result.stderr.lower() if result.stderr else ""
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg:
                wait_time = (2 ** attempt) * 32
                log(f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            log(f"Gemini CLI Error: {result.stderr}")
            return None

        except Exception as e:
            log(f"Execution failed: {e}")
            return None
    
    log("FATAL: Max retries exceeded.")
    return None

def extract_json(text):
    if not text: return None
    try:
        import re
        match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except: pass
    return None

def process_batch_with_session(args):
    """Worker function for processing a single batch using a resumed session."""
    batch_index, total_batches, batch_claims, session_id = args
    log(f"--- Processing Batch {batch_index+1}/{total_batches} (Session: {session_id[:8]}...) ---")
    
    try:
        persona_instructions = load_persona("forensic_auditor_persona", ORCHESTRATOR_DIR)
    except Exception as e:
        log(f"Failed to load forensic_auditor_persona: {e}")
        return None

    # Turn 2 Prompt: Activate Identity + Task
    prompt = (
        f"# ACTIVATING IDENTITY\n{persona_instructions}\n\n"
        "# EXECUTION ORDER\n"
        "Verify the following claims against the CV DATA in your history. Return a JSON array of findings.\n\n"
        f"```json\n{json.dumps(batch_claims, indent=2)}\n```"
    )
    
    response_text = call_agent(prompt, session_id=session_id)
    return extract_json(response_text)

def run_investigation(resume_path, context_text, resume_mode=False, parent_session_id=None):
    with open(resume_path, 'r') as f:
        resume_data = json.load(f)
    
    # --- REGRESSION TESTING START ---
    regressions_path = os.path.join(os.path.dirname(__file__), "known_regressions.json")
    regression_failures = []
    
    if os.path.exists(regressions_path):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running Regression Tests...")
        with open(regressions_path, 'r') as f:
            regressions = json.load(f)

        for rule in regressions:
            field_path = rule['target_field'].split('.')
            
            def get_values(data, keys):
                if not keys: return [data]
                key = keys[0]
                remaining = keys[1:]
                found_values = []
                if isinstance(data, dict):
                    if key in data: found_values.extend(get_values(data[key], remaining))
                elif isinstance(data, list):
                    for item in data: found_values.extend(get_values(item, remaining))
                return found_values

            target_values = get_values(resume_data, field_path)
            
            for value in target_values:
                if not value: continue
                items_to_check = value if isinstance(value, list) else [value]
                for item_val in items_to_check:
                    if not isinstance(item_val, str): continue
                    failed = False
                    if rule['check_type'] == 'regex':
                        import re
                        if not re.match(rule['pattern'], item_val): failed = True
                    elif rule['check_type'] == 'heuristic':
                        try:
                            if not eval(rule['condition'], {"value": item_val, "len": len}): failed = True
                        except: pass
                    if failed:
                        regression_failures.append({
                            "id": rule['id'], "severity": rule['severity'], 
                            "name": rule['name'], "message": rule['error_message']
                        })

    if regression_failures:
        log("⚠️ REGRESSION FAILURES DETECTED")
        base, _ = os.path.splitext(resume_path)
        reg_report_path = f"{base}_REGRESSION_REPORT.md"
        with open(reg_report_path, 'w') as f:
            f.write("# Regression Test Failures\n\n| Status | Severity | Rule | Message |\n|---|---|---|---|")
            for fail in regression_failures:
                f.write(f"| FAIL | {fail['severity']} | {fail['name']} | {fail['message']} |\n")
        log(f"Regression report saved to {reg_report_path}")

    claims = flatten_resume(resume_data)
    
    # --- SMART DELTA AUDIT ---
    filename = os.path.basename(resume_path)
    cache_file = os.path.join(TMP_DIR, f"audit_cache_{filename}.json")
    
    cached_findings = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                loaded = json.load(f)
                for item in loaded:
                    if item.get('claim'): cached_findings[item['claim']] = item
            log(f"Loaded {len(cached_findings)} verified claims from cache.")
        except Exception as e:
            log(f"Cache load error: {e}")

    claims_to_audit = []
    final_findings = []
    
    for c in claims:
        claim_text = c['claim']
        if claim_text in cached_findings and cached_findings[claim_text].get('status') == 'VERIFIED':
            final_findings.append(cached_findings[claim_text])
        else:
            claims_to_audit.append(c)
            
    if not claims_to_audit:
        log("All claims already VERIFIED in cache. Skipping API calls.")
        return final_findings, regression_failures

    log(f"Delta Audit: {len(final_findings)} reused, {len(claims_to_audit)} new/modified claims to verify.")
    
    # --- PARALLEL EXECUTION WITH SESSION POOL ---
    total_batches = math.ceil(len(claims_to_audit) / BATCH_SIZE)
    required_sessions = min(MAX_WORKERS, total_batches)
    
    # Pass parent_session_id to init_session_pool
    session_pool = init_session_pool(context_text, required_sessions, parent_session_id=parent_session_id)
    
    if not session_pool:
        log("FATAL: Could not initialize any sessions.")
        return None, regression_failures

    batch_args = []
    for i in range(total_batches):
        batch_start = i * BATCH_SIZE
        batch_end = min(batch_start + BATCH_SIZE, len(claims_to_audit))
        current_batch = claims_to_audit[batch_start:batch_end]
        assigned_session = session_pool[i % len(session_pool)]
        batch_args.append((i, total_batches, current_batch, assigned_session))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(session_pool)) as executor:
        results = list(executor.map(process_batch_with_session, batch_args))

    for res in results:
        if res:
            final_findings.extend(res)
            for f in res:
                 if f.get('claim'): cached_findings[f['claim']] = f
    
    with open(cache_file, 'w') as f:
        json.dump(list(cached_findings.values()), f, indent=2)
            
    return final_findings, regression_failures

def run_final_audit(findings, regression_failures, output_path):
    log("Starting Final Auditor Review...")
    
    exceptions = [f for f in findings if f.get('status') != 'VERIFIED']
    
    if not exceptions and not regression_failures:
        log("No exceptions found. All claims VERIFIED.")
        success_msg = "# Final Audit Report\n\n**Result:** PASS\n\nAll claims in the resume were verified against the provided context."
        with open(output_path, "w") as f:
            f.write(success_msg)
        result_path = output_path.replace("_AUDIT_REPORT.md", "_audit_result.json")
        with open(result_path, "w") as f:
            json.dump({"status": "PASS", "failed_claims": [], "regression_failures": []}, f)
        print(success_msg)
        return

    log(f"Filtered {len(findings)} claims down to {len(exceptions)} exceptions for review.")

    full_report = ""
    if exceptions:
        try:
            persona_instructions = load_persona("qa_auditor_persona", ORCHESTRATOR_DIR)
            prompt = (
                f"# ACTIVATING IDENTITY\n{persona_instructions}\n\n"
                "# EXECUTION ORDER\n"
                "Review these exceptions. If they are plausible based on the context, mark them verified. If not, explain why.\n\n"
                f"```json\n{json.dumps(exceptions, indent=2)}\n```"
            )
            # This QA step is usually single-shot (no deep context required, just logic), 
            # or could use a session if we wanted deep verification. For now, basic single shot is fine.
            
            response_text = call_agent(prompt) 
            if response_text:
                full_report += response_text
        except Exception as e:
            log(f"Failed to load qa_auditor_persona or run final review: {e}")
            for ex in exceptions:
                full_report += f"- {ex.get('status')}: {ex.get('claim')}\n"
    
    if regression_failures:
        full_report += "\n\n## Regression Failures\n\n"
        for fail in regression_failures:
            full_report += f"- **{fail['severity']}**: {fail['message']} (Rule: {fail['name']})\n"

    with open(output_path, "w") as f:
        f.write(full_report)
        
    result_path = output_path.replace("_AUDIT_REPORT.md", "_audit_result.json")
    with open(result_path, "w") as f:
        json.dump({
            "status": "FAIL", 
            "failed_claims": exceptions,
            "regression_failures": regression_failures,
            "failure_type": "REGRESSION" if regression_failures else "FORENSIC"
        }, f, indent=2)

    print("\n" + "="*30 + "\n FINAL EXCEPTION REPORT \n" + "="*30 + "\n")
    print(full_report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_file", help="Path to the resume JSON file")
    parser.add_argument("--output", "-o", help="Output file. Defaults to <resume_filename>_AUDIT_REPORT.md")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint if available. Default is start fresh.")
    parser.add_argument("--parent-session-id", help="UUID of an existing initialized Master Session to fork workers from.")
    args = parser.parse_args()
    
    ensure_tmp_dir()

    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.resume_file)
        output_path = f"{base}_AUDIT_REPORT.md"

    # Only load context text if we don't have a parent session (fallback mode)
    context_text = ""
    if not args.parent_session_id:
        context_text = load_context(CV_DATA_DIR)

    findings, regression_failures = run_investigation(
        args.resume_file, 
        context_text, 
        resume_mode=args.resume,
        parent_session_id=args.parent_session_id
    )
    
    if findings is not None:
        run_final_audit(findings, regression_failures, output_path)
args.parent_session_id:
        context_text = load_context(CV_DATA_DIR)

    findings, regression_failures = run_investigation(
        args.resume_file, 
        context_text, 
        resume_mode=args.resume,
        parent_session_id=args.parent_session_id
    )
    
    if findings is not None:
        run_final_audit(findings, regression_failures, output_path)
