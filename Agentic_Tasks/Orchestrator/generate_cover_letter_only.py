import os
import sys
import json
import subprocess
from utils.context_loader import load_cv_context, load_persona

# Configuration
MODEL = "gemini-3.1-pro-preview"
ORCHESTRATOR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ORCHESTRATOR_DIR))
CV_DATA_DIR = os.path.join(PROJECT_ROOT, "cv-data")
RESUMES_DIR = os.path.join(PROJECT_ROOT, "cv-data", "resumes")

import time

MAX_RETRIES = 5

def call_gemini(system_prompt, user_input):
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    cmd = ["gemini", "--model", MODEL, "--output-format", "text"]
    
    backoff_times = [20, 60, 180, 600]
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
                time.sleep(10) # Add delay between requests
                return result.stdout.strip()

            # Error handling
            err_msg = result.stderr.lower() if result.stderr else ""
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg or result.returncode != 0:
                if attempt == MAX_RETRIES - 1:
                    break # Exit loop immediately on final failure
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
                print(f"[WARN] Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
                print("[INFO] Resuming execution after backoff...")
                continue
            
            print(f"Error: {result.stderr}")
            return None

        except subprocess.TimeoutExpired:
            print("subprocess.TimeoutExpired: Gemini CLI hung.")
            continue
        except subprocess.TimeoutExpired:
            print("WARN" if "print" in globals() else "print", f"Gemini API Timeout (Attempt {attempt+1}/{MAX_RETRIES}). Backing off...")
            time.sleep(backoff_times[attempt] if attempt < len(backoff_times) else 600)
            continue
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    print("[FATAL] Max retries exceeded.")
    return None

def generate_cover_letter(resume_path, jd_path):
    print("Loading context...")
    with open(resume_path, 'r') as f:
        resume_json = json.load(f)
    with open(jd_path, 'r') as f:
        jd_text = f.read()
    
    cv_context = load_cv_context(CV_DATA_DIR)
    cl_persona = load_persona("cover_letter_persona", ORCHESTRATOR_DIR)
    
    print("Drafting Cover Letter...")
    cl_input = f"### JOB DESCRIPTION ###\n{jd_text}\n\n### GENERATED RESUME ###\n{json.dumps(resume_json)}\n\n### CANDIDATE CONTEXT ###\n{cv_context}"
    
    cl_text = call_gemini(cl_persona, cl_input)
    
    if cl_text:
        base_name = os.path.basename(resume_path).replace("-resume.json", "")
        # Clean text for TXT output
        clean_text = cl_text.replace("**", "").replace("# ", "").replace("## ", "").replace("`", "")
        cl_txt_path = os.path.join(RESUMES_DIR, f"{base_name}-cover_letter.txt")
        
        with open(cl_txt_path, 'w') as f:
            f.write(clean_text)
        print(f"Cover Letter saved to {cl_txt_path}")
        
        # Convert to PDF
        import shutil
        pandoc_exe = shutil.which("pandoc")
        if pandoc_exe:
            cl_pdf_path = cl_txt_path.replace(".txt", ".pdf")
            try:
                defaults_file = os.path.join(PROJECT_ROOT, "Agentic_Tasks/Format_Conversion/pandoc_defaults.yaml")
                cmd = [pandoc_exe, "-f", "markdown", "-o", cl_pdf_path]
                if os.path.exists(defaults_file): cmd.extend(["--defaults", defaults_file])
                
                subprocess.run(cmd, input=cl_text, text=True, check=True)
                print(f"Cover Letter PDF generated: {cl_pdf_path}")
            except Exception as e:
                print(f"Failed to convert Cover Letter to PDF: {e}")
    else:
        print("Failed to generate cover letter.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", required=True, help="Path to Resume JSON")
    parser.add_argument("--jd", required=True, help="Path to Job Description TXT")
    args = parser.parse_args()
    
    generate_cover_letter(args.resume, args.jd)