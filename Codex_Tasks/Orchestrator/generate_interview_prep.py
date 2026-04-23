import os
import sys
import argparse
import subprocess
import json
import glob
from datetime import datetime

# Configuration
ORCHESTRATOR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ORCHESTRATOR_DIR))
CV_DATA_PATH = os.path.join(PROJECT_ROOT, "cv-data", "resumes", "full_cv_data_latest.md")
RESUMES_DIR = os.path.join(PROJECT_ROOT, "cv-data", "resumes")
PERSONA_PATH = os.path.join(ORCHESTRATOR_DIR, "personas", "interview_prep_persona.md")

def log(msg):
    print(f"[PREP] {msg}", flush=True)

def call_codex(system_prompt, user_input):
    cmd = ["codex", "exec", "--model", "gpt-5.4-mini", "--color", "never", "-"]
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    try:
        result = subprocess.run(
            cmd, 
            input=full_prompt, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            log(f"Codex Error: {result.stderr}")
            if result.stdout:
                print(result.stdout, flush=True)
            return None
    except Exception as e:
        log(f"Execution Error: {e}")
        return None

def find_related_resumes(company_name):
    # Simple search in cv-data/resumes/ and cv-data/resumes/archive
    matches = []
    # Search for files containing company name
    files = glob.glob(os.path.join(RESUMES_DIR, f"*{company_name}*.json"))
    files += glob.glob(os.path.join(RESUMES_DIR, "archive", f"*{company_name}*.json"))
    
    content = ""
    for f in files[:3]: # Limit to top 3
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
                content += f"\n--- PAST RESUME: {os.path.basename(f)} ---\n{json.dumps(data, indent=2)}\n"
        except: pass
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", required=True, help="Path to Job Description file")
    parser.add_argument("--company", required=True, help="Company Name")
    parser.add_argument("--position", required=True, help="Position Title")
    parser.add_argument("--notes", help="Additional research notes to include in the dossier")
    args = parser.parse_args()

    # 1. Load Persona
    try:
        with open(PERSONA_PATH, 'r') as f:
            persona = f.read()
    except Exception as e:
        log(f"Error loading persona: {e}")
        sys.exit(1)

    # 2. Load JD
    try:
        with open(args.jd, 'r') as f:
            jd_text = f.read()
    except Exception as e:
        log(f"Error loading JD: {e}")
        sys.exit(1)

    # 3. Load CV Data
    cv_data = "[Full CV Data Missing]"
    if os.path.exists(CV_DATA_PATH):
        try:
            with open(CV_DATA_PATH, 'r') as f:
                cv_data = f.read()
        except: pass
    else:
        log("WARN: full_cv_data_latest.md not found.")

    # 4. Find Past Resumes
    past_resumes = find_related_resumes(args.company)

    # 5. Construct Prompt
    input_data = f"### RESEARCH NOTES\n{args.notes}\n\n### TARGET ROLE\n**Company:** {args.company}\n**Position:** {args.position}\n\n### JOB DESCRIPTION\n{jd_text}\n\n### PAST RESUMES (Context)\n{past_resumes}\n\n### FULL CANDIDATE HISTORY (CV DATA)\n{cv_data}"

    log("Analyzing profile and generating dossier...")
    dossier = call_codex(persona, input_data)

    if dossier:
        # Strip everything before #BEGIN# marker
        if "#BEGIN#" in dossier:
            dossier = dossier.split("#BEGIN#", 1)[1].strip()

        # Clean dossier of markdown code block wrappers if they exist
        if dossier.startswith("```markdown"):
            dossier = dossier[len("```markdown"):].strip()
        if dossier.startswith("```"):
            dossier = dossier[len("```"):].strip()
        if dossier.endswith("```"):
            dossier = dossier[:-len("```")].strip()

        filename_base = f"{args.position.replace(' ', '-')}-{args.company.replace(' ', '-')}-Interview-Prep"
        jd_dir = RESUMES_DIR
        output_path = os.path.join(jd_dir, f"{filename_base}.md")
        pdf_path = os.path.join(jd_dir, f"{filename_base}.pdf")
        
        with open(output_path, 'w') as f:
            f.write(dossier)
        
        # PDF Generation (MD -> HTML -> PDF for best emoji/formatting support)
        temp_html = os.path.join(jd_dir, f"{filename_base}.html")
        html_to_pdf_script = os.path.join(PROJECT_ROOT, "Codex_Tasks/Format_Conversion/html_to_pdf.py")
        python_exe = sys.executable

        try:
            # 1. MD to HTML
            subprocess.run(["pandoc", output_path, "-o", temp_html], check=True)
            # 2. HTML to PDF
            subprocess.run([python_exe, html_to_pdf_script, temp_html, pdf_path], check=True)
            # 3. Cleanup HTML
            if os.path.exists(temp_html):
                os.remove(temp_html)
            
            log("PDF generated:")
            print(f"file://{os.path.abspath(pdf_path)}")
        except Exception as e:
            log(f"Error generating PDF: {e}")
            if os.path.exists(temp_html):
                os.remove(temp_html)

        print("\n" + "="*40)
        print(dossier)
        print("="*40 + "\n")
    else:
        log("Failed to generate dossier.")

if __name__ == "__main__":
    main()
