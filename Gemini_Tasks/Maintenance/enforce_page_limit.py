import os
import sys
import json
import subprocess
import argparse
import time
import re

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RESUMES_DIR = os.path.join(PROJECT_ROOT, "cv-data", "resumes")
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "bin", "python3")
HTML_TO_PDF_SCRIPT = os.path.join(PROJECT_ROOT, "Gemini_Tasks/Format_Conversion/html_to_pdf.py")

# Add Maintenance dir to path so we can import detect_orphans
sys.path.append(os.path.join(PROJECT_ROOT, "Gemini_Tasks", "Maintenance"))
try:
    from detect_orphans import detect_widows_and_orphans
except ImportError:
    def detect_widows_and_orphans(pdf_path): return []

# Ensure resume-cli is available
RESUME_CLI = os.path.join(PROJECT_ROOT, "node_modules", ".bin", "resume")
if not os.path.exists(RESUME_CLI):
    RESUME_CLI = "resume"

def log(level, message):
    print(f"[{level.upper()}] {message}", flush=True)

def call_gemini(system_prompt, user_input, max_retries=3):
    """Calls Gemini API with exponential backoff."""
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    cmd = ["gemini", "-e", "", "--model", "gemini-3.1-pro-preview", "--output-format", "text"]
    
    # Try to use master session if available in env
    session_id = os.environ.get('MASTER_SESSION_ID')
    if session_id:
        cmd.extend(["--resume", session_id])
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                cmd, 
                input=full_prompt, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                check=False,
                timeout=1800
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            err_msg = result.stderr.lower() if result.stderr else ""
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg or result.returncode != 0:
                wait_time = (2 ** attempt) * 15
                log("WARN", f"Gemini API Error (Attempt {attempt+1}/{max_retries}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            log("ERROR", f"Gemini CLI failed: {result.stderr}")
            return None
            
        except Exception as e:
            log("ERROR", f"Execution exception: {e}")
            return None
    return None

class PageLimitEnforcer:
    def __init__(self, json_path, output_pdf_path, max_pages=2, jd_path=None):
        self.json_path = json_path
        self.output_pdf_path = output_pdf_path
        self.max_pages = max_pages
        self.base_name = os.path.basename(json_path).replace(".json", "")
        self.jd_path = jd_path
        
        # Load JSON
        with open(json_path, 'r') as f:
            self.current_json = json.load(f)

    def get_pdf_page_count(self, pdf_path):
        """Returns number of pages using pdfinfo."""
        try:
            result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "Pages:" in line:
                    return int(line.split(":")[1].strip())
        except Exception as e:
            log("WARN", f"Failed to get page count: {e}")
        return 999 

    def render(self, scale, margin, hide_sections=[]):
        """Renders the PDF with specific settings."""
        temp_html = os.path.join(RESUMES_DIR, f"{self.base_name}_enforce_tmp.html")
        temp_json = os.path.join(RESUMES_DIR, f"{self.base_name}_enforce_tmp.json")
        
        # Save current JSON state
        with open(temp_json, 'w') as f:
            json.dump(self.current_json, f, indent=2)

        # Export HTML
        theme_path = "./custom-resume-theme"
        subprocess.run(
            [RESUME_CLI, "export", temp_html, "--theme", theme_path, "--resume", temp_json], 
            capture_output=True, check=True
        )

        # HTML -> PDF
        cmd = [
            VENV_PYTHON, HTML_TO_PDF_SCRIPT,
            temp_html, self.output_pdf_path,
            "--scale", str(scale),
            "--margin", margin
        ]
        if hide_sections:
            cmd.extend(["--hide"] + hide_sections)

        subprocess.run(cmd, capture_output=True, check=True)
        return self.output_pdf_path

    def get_ai_exclusion_recommendations(self, overflow_pages):
        log("AI", f"Requesting exclusion recommendations (Target overflow: {overflow_pages} pages)")
        
        pruner_persona_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Orchestrator', 'personas', 'resume_pruner_persona.md')
        system_prompt = ""
        if os.path.exists(pruner_persona_path):
             with open(pruner_persona_path, 'r') as f:
                 system_prompt = f.read()

        jd_content = ""
        if self.jd_path and os.path.exists(self.jd_path):
            with open(self.jd_path, 'r') as f:
                jd_content = f"### TARGET JOB DESCRIPTION ###\n{f.read()}\n\n"

        task = f"{jd_content}### MAGNITUDE ###\nThe resume is over the limit by {overflow_pages} pages. Provide enough exclusions to resolve this.\n\n### DRAFT RESUME JSON ###\n{json.dumps(self.current_json, indent=2)}"
        
        raw_response = call_gemini(system_prompt, task)
        if not raw_response: return []

        # Extract JSON
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
        parsed = None
        if match:
            try: parsed = json.loads(match.group(1))
            except: pass
        if not parsed:
            try: 
                start = raw_response.find('{')
                end = raw_response.rfind('}')
                if start != -1 and end != -1:
                    parsed = json.loads(raw_response[start:end+1])
            except: pass
            
        if parsed and "exclusions" in parsed:
            return parsed["exclusions"]
        return []

    def execute_exclusion(self, op):
        op_type = op.get("type")
        target_section = op.get("target_section")
        
        if op_type == "remove_section" and target_section:
            if target_section in self.current_json:
                log("EXCLUDE", f"Section '{target_section}' (Reason: {op.get('reason')})")
                del self.current_json[target_section]
                return True

        elif op_type == "remove_job":
            target_company = op.get("target_company")
            if "work" in self.current_json:
                for i, job in enumerate(self.current_json["work"]):
                    if target_company and target_company.lower() in job.get("name", "").lower():
                        log("EXCLUDE", f"Job '{target_company}' (Reason: {op.get('reason')})")
                        self.current_json["work"].pop(i)
                        return True
        
        elif op_type == "remove_project":
            target_proj = op.get("target_project")
            if "projects" in self.current_json:
                for i, proj in enumerate(self.current_json["projects"]):
                    if target_proj and target_proj.lower() in proj.get("name", "").lower():
                        log("EXCLUDE", f"Project '{target_proj}' (Reason: {op.get('reason')})")
                        self.current_json["projects"].pop(i)
                        return True

        elif op_type == "remove_bullet":
            target_company = op.get("target_company")
            bullet_text = op.get("bullet_text", "")
            if "work" in self.current_json and bullet_text:
                for job in self.current_json["work"]:
                    if target_company and target_company.lower() not in job.get("name", "").lower():
                        continue
                    if "highlights" in job:
                        for i, highlight in enumerate(job["highlights"]):
                            if bullet_text[:30].lower() in highlight.lower():
                                log("EXCLUDE", f"Bullet from '{target_company}' (Reason: {op.get('reason')})")
                                job["highlights"].pop(i)
                                return True
        return False

    def try_layout_optimization(self):
        """Step-up Layout Optimization. Start at minimums, increase until overflow."""
        scales = [0.99, 1.0]
        margins = ["0.5in", "0.6in", "0.7in", "0.8in", "0.9in", "1.0in"]

        min_scale = scales[0]
        min_margin = margins[0]
        
        self.render(min_scale, min_margin, [])
        baseline_pages = self.get_pdf_page_count(self.output_pdf_path)
        log("INFO", f"Baseline check: Scale {min_scale}, Margin {min_margin} -> Pages: {baseline_pages}")

        if baseline_pages > self.max_pages:
            return None # Does not fit
            
        last_valid = {"scale": min_scale, "margin": min_margin, "hidden_sections": []}
        
        for scale in scales:
            for margin in margins:
                if scale == min_scale and margin == min_margin: continue
                    
                self.render(scale, margin, []) 
                current_pages = self.get_pdf_page_count(self.output_pdf_path)
                log("INFO", f"Step-Up check: Scale {scale}, Margin {margin} -> Pages: {current_pages}")
                
                if current_pages <= self.max_pages:
                    last_valid = {"scale": scale, "margin": margin, "hidden_sections": []}
                else:
                    log("SUCCESS", f"Overflow at Scale {scale}, Margin {margin}. Locking in: Scale {last_valid['scale']}, Margin {last_valid['margin']}")
                    self.render(last_valid['scale'], last_valid['margin'], [])
                    return last_valid
                    
        log("SUCCESS", f"Max settings achieved. Locking in: Scale {last_valid['scale']}, Margin {last_valid['margin']}")
        self.render(last_valid['scale'], last_valid['margin'], [])
        return last_valid

    def micro_prune_orphans(self, pdf_path, margin, scale):
        """Phase 3: Detects orphan words and uses AI to shorten the exact strings."""
        orphans = detect_widows_and_orphans(pdf_path)
        if not orphans:
            log("INFO", "Phase 3 (Typesetting): No orphans detected. Typography is clean.")
            return False

        log("INFO", f"Phase 3 (Typesetting): Detected {len(orphans)} wrapped lines at locked layout. Invoking micro-pruning...")
        
        system_prompt = "You are a typesetting AI. Shorten the provided sentence to prevent line-wrapping by dropping the exact number of characters requested. Preserve all meaning and ATS keywords. Output ONLY the raw new string. No formatting, no explanations."
        
        json_str = json.dumps(self.current_json, indent=2)
        changes = False
        
        for orphan in orphans:
            orig = orphan['original_text']
            target_save = orphan['chars_to_save']
            
            # Flexible exact match search
            escaped_orig = re.escape(orig).replace(r'\ ', r'\s+')
            match = re.search(escaped_orig, json_str)
            if not match and len(orig) > 60:
                 start_part = re.escape(orig[:30]).replace(r'\ ', r'\s+')
                 end_part = re.escape(orig[-30:]).replace(r'\ ', r'\s+')
                 match = re.search(f"{start_part}.*?{end_part}", json_str, re.DOTALL)
            
            if match:
                exact_json_string = match.group(0)
                task = f"Shorten this by {target_save + 3} to {target_save + 10} characters. It MUST be shorter. Original: {exact_json_string}"
                
                shortened = call_gemini(system_prompt, task, max_retries=2)
                
                if shortened and len(shortened) < len(exact_json_string):
                    log("FIX", f"Orphan Pruned: '{exact_json_string[:30]}...' -> '{shortened[:30]}...' (Saved {len(exact_json_string) - len(shortened)} chars)")
                    json_str = json_str.replace(exact_json_string, shortened)
                    changes = True
                else:
                    log("WARN", f"AI failed to meaningfully shorten orphan: '{orig[:30]}...'")
        
        if changes:
            try:
                self.current_json = json.loads(json_str)
                return True
            except json.JSONDecodeError as e:
                log("ERROR", f"Micro-pruning JSON decode error: {e}")
                
        return False

    def backup_json(self, suffix):
        """Creates a backup of the current JSON."""
        backup_path = self.json_path.replace(".json", f"_{suffix}.json")
        with open(backup_path, 'w') as f:
            json.dump(self.current_json, f, indent=2)
        log("INFO", f"Created backup: {os.path.basename(backup_path)}")

    def enforce(self):
        log("START", f"Enforcing {self.max_pages}-page limit for {self.base_name}")
        self.backup_json("pre_resize")
        
        # --- PHASE 1 & 2: Magnitude-Aware Multi-Pass Exclusions ---
        loop_limit = 5
        for attempt in range(loop_limit):
            self.render(0.99, "0.5in", [])
            current_pages = self.get_pdf_page_count(self.output_pdf_path)
            
            if current_pages <= self.max_pages:
                log("PASS", "Document fits baseline constraints.")
                break
                
            overflow = current_pages - self.max_pages
            log("PHASE", f"Macro-Layout: Over limit by {overflow} pages. Requesting exclusions...")
            
            exclusions = self.get_ai_exclusion_recommendations(overflow)
            if not exclusions:
                log("FAIL", "Recommender failed to provide exclusions.")
                return False
                
            # Apply all exclusions in batch
            any_success = False
            for op in exclusions:
                if self.execute_exclusion(op):
                    any_success = True
                    
            if not any_success:
                log("FAIL", "Failed to apply any recommended exclusions. Aborting to prevent loop.")
                return False
        else:
            log("FAIL", "Max exclusion iterations reached. Could not enforce limit.")
            return False
            
        # --- PHASE 3: Locked Layout Typesetting ---
        log("PHASE", "Locking Layout Constraints...")
        winning_settings = self.try_layout_optimization()
        if not winning_settings:
            log("ERROR", "Unexpected layout failure after baseline pass.")
            return False
            
        # --- PHASE 4: Final Polish (Orphans) ---
        if self.micro_prune_orphans(self.output_pdf_path, winning_settings["margin"], winning_settings["scale"]):
            log("PHASE", "Final Polish: Re-rendering with shortened strings.")
            self.render(winning_settings["scale"], winning_settings["margin"], [])

        self.save_result(winning_settings)
        return True

    def save_result(self, settings):
        with open(self.json_path, 'w') as f:
            json.dump(self.current_json, f, indent=2)

        settings_path = self.json_path.replace(".json", ".render_settings.json")
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        log("SAVE", f"Render settings saved to {settings_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="Path to resume JSON")
    parser.add_argument("output_pdf", help="Path to output PDF")
    parser.add_argument("--jd", help="Path to Job Description (for AI context)", default=None)
    args = parser.parse_args()

    enforcer = PageLimitEnforcer(args.json_path, args.output_pdf, jd_path=args.jd)
    if not enforcer.enforce():
        sys.exit(1)