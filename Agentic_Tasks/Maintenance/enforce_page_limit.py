import os
import sys
import json
import subprocess
import argparse
import time

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RESUMES_DIR = os.path.join(PROJECT_ROOT, "cv-data", "resumes")
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "bin", "python3")
HTML_TO_PDF_SCRIPT = os.path.join(PROJECT_ROOT, "Agentic_Tasks/Format_Conversion/html_to_pdf.py")

# Ensure resume-cli is available
RESUME_CLI = os.path.join(PROJECT_ROOT, "node_modules", ".bin", "resume")
if not os.path.exists(RESUME_CLI):
    RESUME_CLI = "resume"

def log(level, message):
    print(f"[{level.upper()}] {message}", flush=True)

def call_gemini(system_prompt, user_input):
    """Calls Gemini API with exponential backoff."""
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    cmd = ["gemini", "--model", "gemini-3-flash-preview", "--output-format", "text"]
    MAX_RETRIES = 5
    
    for attempt in range(MAX_RETRIES):
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
                wait_time = (2 ** attempt) * 32 
                log("WARN", f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s...")
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

        # Settings
        self.MARGINS = ["1.0in", "0.9in", "0.8in", "0.7in", "0.6in", "0.5in"]
        self.SCALES = [1.0, 0.99] # Removed 0.98 to keep scaling minimal
        self.REMOVABLE_SECTIONS = [
            "interests", 
            "languages", 
            "publications", 
            "volunteer", 
            "education", 
            "awards"
        ]

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

    def get_overflow_lines(self, pdf_path, target_page=3):
        """Counts lines on the specific overflow page."""
        try:
            cmd = ["pdftotext", "-f", str(target_page), "-l", str(target_page), pdf_path, "-"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                lines = [l for l in result.stdout.splitlines() if l.strip()]
                return len(lines)
        except:
            pass
        return 0

    def render(self, scale, margin, hide_sections):
        """Renders the PDF with specific settings."""
        temp_html = os.path.join(RESUMES_DIR, f"{self.base_name}_enforce_tmp.html")
        temp_json = os.path.join(RESUMES_DIR, f"{self.base_name}_enforce_tmp.json")
        
        # Save current JSON state
        with open(temp_json, 'w') as f:
            json.dump(self.current_json, f, indent=2)

        # Export HTML
        # Use relative path for custom theme to ensure compatibility
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

    def get_word_count(self, data=None):
        if data is None: data = self.current_json
        text_dump = []
        def extract_text(obj):
            if isinstance(obj, str): text_dump.append(obj)
            elif isinstance(obj, list):
                for item in obj: extract_text(item)
            elif isinstance(obj, dict):
                for val in obj.values(): extract_text(val)
        extract_text(data)
        all_text = " ".join(text_dump).replace("**", "").replace("#", "").replace("-", " ")
        words = [w for w in clean_text.split() if w.strip()] if 'clean_text' in locals() else all_text.split()
        return len(words)

    def ai_prune_bullets(self, overflow_pages):
        """Prunes bullets using AI as a last resort."""
        log("AI", f"Invoking AI to prune content (Overflow pages: {overflow_pages})...")
        
        jd_context = ""
        if self.jd_path and os.path.exists(self.jd_path):
            with open(self.jd_path, 'r') as f:
                jd_context = f"\n### JOB DESCRIPTION ###\n{f.read()[:2000]}..."

        # If overflow is massive, programmatically drop the oldest work entry to save tokens/time
        if overflow_pages > 5:
             if "work" in self.current_json and len(self.current_json["work"]) > 3:
                 log("WARN", "Massive overflow. Programmatically dropping oldest work entry.")
                 self.current_json["work"].pop()
                 return True
             if "projects" in self.current_json and len(self.current_json["projects"]) > 3:
                 log("WARN", "Massive overflow. Programmatically dropping oldest project entry.")
                 self.current_json["projects"].pop()
                 return True

        pruner_persona_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Orchestrator', 'personas', 'resume_pruner_persona.md')
        
        # Prepare the stdin for the gemini call
        jd_persona_header = f"""---
name: position description
description: The full text of the job description to be used for relevance scoring.
---
"""
        jd_content = ""
        if self.jd_path and os.path.exists(self.jd_path):
            with open(self.jd_path, 'r') as f:
                jd_content = f.read()

        # Combine the pruner persona, the JD persona, and the JD content for stdin
        # This uses the shell piping technique to combine multiple inputs for the gemini tool
        import shlex
        safe_jd_content = shlex.quote(f"{jd_persona_header}\n{jd_content}")
        gemini_stdin_content = f"cat {pruner_persona_path} <(echo -e {safe_jd_content})"
        
        # If the JSON is too large, it might fail. We only send the work and projects.
        subset = {
            "work": self.current_json.get("work", []),
            "projects": self.current_json.get("projects", [])
        }
        
        # Construct the task prompt
        task_prompt = f"""You have been provided with the full candidate CV data in your session history. Now, review the following oversized resume and prune it according to your persona's rules.
        
### OVERSIZED RESUME (JSON) ###
{json.dumps(subset)}
"""
        safe_task_prompt = shlex.quote(task_prompt)

        # Build the final gemini command
        cmd = [
            "bash",
            "-c",
            f"{gemini_stdin_content} | gemini --resume {os.environ.get('MASTER_SESSION_ID')} -p {safe_task_prompt}"
        ]
        
        result_text = ""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            result_text = result.stdout
        except subprocess.CalledProcessError as e:
            log("ERROR", f"AI Pruning Gemini call failed: {e.stderr}")
            return False
        except Exception as e:
            log("ERROR", f"An unexpected error occurred during AI Pruning: {e}")
            return False
        
        if result_text:
            import re
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            parsed = None
            if match:
                try: parsed = json.loads(match.group(1))
                except: pass
            if not parsed:
                try: parsed = json.loads(result_text)
                except: pass
                
            if parsed:
                if "work" in parsed:
                    self.current_json["work"] = parsed["work"]
                if "projects" in parsed:
                    self.current_json["projects"] = parsed["projects"]
                return True
            
        log("ERROR", "AI Pruning failed to return valid JSON.")
        return False

    def remove_section(self, section_name):
        """Programmatically removes a section from the JSON."""
        if section_name in self.current_json:
            log("ACTION", f"Removing section: {section_name}")
            del self.current_json[section_name]
            return True
        return False

    def try_layout_optimization(self):
        """Step-up Layout Optimization. Start at minimums, increase until overflow."""
        # Sorted from smallest to largest
        scales = [0.99, 1.0]
        margins = ["0.5in", "0.6in", "0.7in", "0.8in", "0.9in", "1.0in"]

        # Baseline check (minimum settings)
        min_scale = scales[0]
        min_margin = margins[0]
        
        try:
            self.render(min_scale, min_margin, [])
            baseline_pages = self.get_pdf_page_count(self.output_pdf_path)
            log("INFO", f"Baseline check: Scale {min_scale}, Margin {min_margin} -> Pages: {baseline_pages}")
        except Exception as e:
            log("WARN", f"Baseline render failed: {e}")
            return None

        if baseline_pages > self.max_pages:
            return None # Does not fit even at minimum settings
            
        # It fits! Now step-up to find the best looking (largest) settings
        last_valid = {"scale": min_scale, "margin": min_margin, "hidden_sections": []}
        
        for scale in scales:
            for margin in margins:
                # Skip the baseline we just checked
                if scale == min_scale and margin == min_margin:
                    continue
                    
                try:
                    self.render(scale, margin, []) 
                    current_pages = self.get_pdf_page_count(self.output_pdf_path)
                    log("INFO", f"Step-Up check: Scale {scale}, Margin {margin} -> Pages: {current_pages}")
                    
                    if current_pages <= self.max_pages:
                        last_valid = {"scale": scale, "margin": margin, "hidden_sections": []}
                    else:
                        # We hit the overflow limit. Return the last valid settings.
                        log("SUCCESS", f"Overflow at Scale {scale}, Margin {margin}. Reverting to Scale: {last_valid['scale']}, Margin: {last_valid['margin']}")
                        # Re-render with last valid before returning
                        self.render(last_valid['scale'], last_valid['margin'], [])
                        return last_valid
                except Exception as e:
                    log("WARN", f"Render or page count failed at Scale {scale}, Margin {margin}: {e}")
                    # If a render fails, we'll just stop stepping up and return last valid
                    self.render(last_valid['scale'], last_valid['margin'], [])
                    return last_valid
                    
        # If we get through all of them and they all fit (e.g. it's a short resume)
        log("SUCCESS", f"Max settings achieved with Scale: {last_valid['scale']}, Margin: {last_valid['margin']}")
        # Ensure final render is the max settings
        self.render(last_valid['scale'], last_valid['margin'], [])
        return last_valid

    def backup_json(self, suffix):
        """Creates a backup of the current JSON."""
        backup_path = self.json_path.replace(".json", f"_{suffix}.json")
        with open(backup_path, 'w') as f:
            json.dump(self.current_json, f, indent=2)
        log("INFO", f"Created backup: {os.path.basename(backup_path)}")

    def enforce(self):
        log("START", f"Enforcing {self.max_pages}-page limit for {self.base_name} (Bottom-Up Optimization)")
        self.backup_json("pre_resize")
        
        # --- PHASE 1 & 2: Loop Section Removal ---
        # We try layout optimization first. If fail, remove a section, try again.
        
        # Make a copy of the list so we can pop from it
        sections_to_remove = list(self.REMOVABLE_SECTIONS)
        
        # We allow one "Layout Pass" before any removal
        # Then N passes where we remove one section each time
        
        max_attempts = len(sections_to_remove) + 1
        
        for i in range(max_attempts):
            log("PHASE", f"Layout Optimization Pass {i+1}...")
            
            winning_settings = self.try_layout_optimization()
            if winning_settings:
                self.save_result(winning_settings)
                return True
            
            log("INFO", "Baseline optimization failed (content too long).")

            # If we are here, layout failed. Remove a section.
            if sections_to_remove:
                next_section = sections_to_remove.pop(0)
                self.backup_json(f"pre_remove_{next_section}")
                if not self.remove_section(next_section):
                    # Section didn't exist, loop immediately to try next
                    continue
            else:
                log("WARN", "All removable sections gone. Still over limit.")
                break

        # --- PHASE 3: AI Pruning (Last Resort) ---
        log("PHASE", "Invoking AI Bullet Pruning (Last Resort)...")
        self.backup_json("pre_ai_pruning")
        
        # Try AI pruning in a loop (up to 5 times)
        for attempt in range(5):
            self.render(0.99, "0.5in", []) # baseline check
            current_pages = self.get_pdf_page_count(self.output_pdf_path)
            if current_pages <= self.max_pages:
                # Need to try layout optimization to step-up
                winning_settings = self.try_layout_optimization()
                if winning_settings:
                    self.save_result(winning_settings)
                    return True
                break
                
            overflow_pages = current_pages - self.max_pages
            if self.ai_prune_bullets(overflow_pages):
                # After pruning, retry layout optimization
                winning_settings = self.try_layout_optimization()
                if winning_settings:
                    self.save_result(winning_settings)
                    return True
            else:
                break # AI failed to produce JSON

        log("FAIL", "Could not enforce page limit.")
        return False

    def save_result(self, settings):
        # Save final JSON
        with open(self.json_path, 'w') as f:
            json.dump(self.current_json, f, indent=2)

        # Save settings
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