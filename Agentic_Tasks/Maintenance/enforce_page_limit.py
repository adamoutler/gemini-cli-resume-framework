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
                check=False
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
            "publications", 
            "education", 
            "volunteer", 
            "languages", 
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

        if overflow_pages > 1:
            instruction = f"The resume is over by {overflow_pages} pages. You MUST remove an entire older job role (not the most recent) AND 5-10 bullet points across remaining roles."
        else:
            instruction = "The resume is slightly over the limit. Remove exactly 2-3 of the LEAST impactful bullet points from older roles."

        prompt = f"""
You are an expert Resume Editor. The resume is too long.
TARGET: Strictly {self.max_pages} pages.

INSTRUCTIONS:
1. {instruction}
2. Identify the LEAST relevant bullet points based on the JD (if provided) or general impact.
3. Rewrite any "widow" lines (bullets wrapping by 1-2 words) to be concise.
4. **CRITICAL:** Do NOT merge, combine, or consolidate separate job entries.

{jd_context}

Return ONLY the valid, shortened JSON.
"""
        # If the JSON is too large, it might fail. We only send the work and projects.
        subset = {
            "work": self.current_json.get("work", []),
            "projects": self.current_json.get("projects", [])
        }
        
        result_text = call_gemini(prompt, json.dumps(subset))
        
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
        """Step 1: Greedy Layout Optimization. Iterate scales, then margins."""
        for scale in self.SCALES:
            for margin in self.MARGINS:
                try:
                    self.render(scale, margin, []) 
                    current_pages = self.get_pdf_page_count(self.output_pdf_path)
                    log("INFO", f"Tested Scale {scale}, Margin {margin} -> Pages: {current_pages}")
                    if current_pages <= self.max_pages:
                        log("SUCCESS", f"Fit achieved with Scale: {scale}, Margin: {margin}")
                        return {"scale": scale, "margin": margin, "hidden_sections": []}
                except Exception as e:
                    log("WARN", f"Render or page count failed at Margin {margin}: {e}")
                    continue
            
        return None

    def enforce(self):
        log("START", f"Enforcing {self.max_pages}-page limit for {self.base_name}")
        
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
            
            log("INFO", "Layout optimization failed for this content set.")

            # If we are here, layout failed. Remove a section.
            if sections_to_remove:
                next_section = sections_to_remove.pop(0)
                if not self.remove_section(next_section):
                    # Section didn't exist, loop immediately to try next
                    continue
            else:
                log("WARN", "All removable sections gone. Still over limit.")
                break

        # --- PHASE 3: AI Pruning (Last Resort) ---
        log("PHASE", "Invoking AI Bullet Pruning (Last Resort)...")
        
        # Try AI pruning in a loop (up to 5 times)
        for attempt in range(5):
            current_pages = self.get_pdf_page_count(self.output_pdf_path)
            if current_pages <= self.max_pages:
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