import json
import os
import sys
import subprocess
import glob
import argparse

# Configuration
MODEL = "gpt-5.4"
CV_DATA_DIR = "./cv-data"

def load_context(data_dir):
    context = []
    files = glob.glob(os.path.join(data_dir, "**/*.md"), recursive=True)
    context.append("---\nBEGIN CV DATA CONTEXT ---")
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                context.append(f"\n---\nFILE: {os.path.basename(filepath)} ---")
                context.append(content)
        except: pass
    context.append("---\nEND CV DATA CONTEXT ---")
    return "\n".join(context)

def call_agent(prompt):
    try:
        # Pass the entire prompt via stdin to avoid "Argument list too long"
        cmd = ["codex", "exec", "--model", MODEL, "--color", "never", "-"]
        result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding='utf-8', check=False, timeout=1800)
        if result.returncode != 0:
            print(f"Codex CLI Error: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"Execution failed: {e}")
        return None

def extract_json(text):
    if not text: return None
    try:
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        
        # Fallback for plain object
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except: pass
    return None

def fix_resume(resume_path, report_path=None):
    with open(resume_path, 'r') as f:
        resume_data = json.load(f)

    validation_context = ""
    if report_path and os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report = json.load(f)
        validation_context = json.dumps(report, indent=2)

    cv_context = load_context(CV_DATA_DIR)

    prompt = f"""
{cv_context}

---\nINSTRUCTION ---
You are a Resume Reliability Engineer.
Your Goal: Fix the provided JSON Resume to comply with the schema and ensure critical career history is present.

INPUT RESUME JSON:
{json.dumps(resume_data, indent=2)}

VALIDATION ERRORS/WARNINGS:
{validation_context}

CRITICAL FIX INSTRUCTIONS:
1. **Schema Repair:** Fix any 'CRITICAL SCHEMA ERRORS' listed above (e.g., date formats YYYY-MM-DD, flat string lists for keywords/highlights).
2. **Legacy Compatibility:** ensure every entry in the 'work' array has a 'company' field. If missing, copy the value from 'name'.
3. **Mandatory History Injection:** Ensure the 'work' or 'volunteer' sections contain entries for the following KEY EXPERIENCE items. If they are missing, GENERATE them using the provided CV DATA CONTEXT.
   - **US Army** (Radar/Biomedical Engineer) -> 'work'
   - **Civil Service** (Government Automation) -> 'work'
   - **CASUAL-Dev** (Founder/Lead Developer) -> 'work'
   - **XDA-Developers** (Elite Recognized Developer) -> 'volunteer' or 'work' (as appropriate)
3. **Missing Sections:** If optional sections (publications, projects, awards) are missing and data exists in the context, create them.
4. **Data Integrity:** Do NOT remove existing valid entries. Merge new requirements in.

OUTPUT:
Return ONLY the corrected valid JSON object.
"""
    print("Requesting Codex to fix resume structure and inject mandatory history...")
    response_text = call_agent(prompt)
    fixed_data = extract_json(response_text)

    if fixed_data:
        print(f"Fix successful. Overwriting {resume_path}")
        with open(resume_path, 'w') as f:
            json.dump(fixed_data, f, indent=2)
    else:
        print("Failed to parse corrected JSON from agent.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_file", help="Path to the resume JSON file")
    parser.add_argument("--report", help="Path to the validation report JSON")
    args = parser.parse_args()

    fix_resume(args.resume_file, args.report)
