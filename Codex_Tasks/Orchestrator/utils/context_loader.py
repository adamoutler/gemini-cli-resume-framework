import os
import glob
import json
import subprocess

DEFAULT_CONTEXT_MODEL = "gpt-5.4-mini"
DEFAULT_TASK_MODEL = "gpt-5.4"

def load_cv_context(data_dir):
    """
    Recursively reads ALL markdown files in the data_dir using os.walk.
    Organizes them into a context stream that mirrors the ATS Resume Schema structure.
    """
    # 1. Scrape all files into memory first
    all_files = {} # { "category_key": [ (rel_path, content), ... ] }
    
    for root, dirs, files in os.walk(data_dir):
        # Ignore the resumes directory to prevent recursive context amplification
        if "resumes" in dirs:
            dirs.remove("resumes")
            
        # Ignore directories containing an EXCLUDE_DIRECTORY file
        if "EXCLUDE_DIRECTORY" in files:
            continue
            
        dirs.sort()
        files.sort()
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, data_dir)
                
                # Determine category based on path and filename
                parts = rel_path.split(os.sep)
                top_folder = parts[0]
                
                category = "other"
                
                if top_folder == "business_logic" or filename == "positions.md":
                    category = "logic"
                elif top_folder == "PROFESSIONAL EXPERIENCE":
                    category = "work"
                elif top_folder == "personal-projects":
                    category = "projects"
                elif top_folder == "authored-articles":
                    category = "publications"
                elif top_folder == "news-media-mentions":
                    category = "media"
                elif top_folder == "general":
                    # Sub-classification for general files
                    fname = filename.lower()
                    if "contact" in fname or "career-goals" in fname or "security-clearance" in fname:
                        category = "basics"
                    elif "career-history" in fname:
                        category = "work"
                    elif "education" in fname: 
                        category = "education"
                    elif "skills" in fname or "reverse-engineering" in fname: 
                        category = "skills"
                    elif "awards" in fname: 
                        category = "awards"
                    elif "patents" in fname:
                        category = "publications"
                    elif "cert" in fname: 
                        category = "certificates"
                    elif "volunteer" in fname or "community" in fname: 
                        category = "volunteer"
                    elif "languages" in fname: 
                        category = "languages"
                    elif "recommendation" in fname or "testimony" in fname: 
                        category = "references"
                    else: 
                        category = "general_misc"
                else:
                    category = top_folder

                if category not in all_files:
                    all_files[category] = []
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        all_files[category].append((rel_path, content))
                except Exception as e:
                    print(f"Warning: Could not read {filepath}: {e}")

    # 2. Construct Context in Resume Schema Order
    context = []
    context.append("--- BEGIN CV KNOWLEDGE BASE (Schema-Aligned) ---")

    # Order matches standard JSON Resume Schema + Logic first
    # (Display Header, Category Key)
    schema_order = [
        ("INSTRUCTIONS & LOGIC", "logic"),
        ("BASICS (Contact, Goals, Clearance)", "basics"),
        ("WORK EXPERIENCE", "work"),
        ("EDUCATION", "education"),
        ("SKILLS", "skills"),
        ("CERTIFICATES", "certificates"),
        ("AWARDS", "awards"),
        ("PROJECTS", "projects"),
        ("PUBLICATIONS (Articles, Patents)", "publications"),
        ("VOLUNTEER", "volunteer"),
        ("LANGUAGES", "languages"),
        ("REFERENCES", "references"),
        ("MEDIA MENTIONS", "media"), # Extra context
        ("GENERAL / MISC", "general_misc")
    ]
    
    processed_categories = set()

    for header, key in schema_order:
        if key in all_files:
            context.append(f"\n### SECTION: {header} ###")
            for rel_path, content in all_files[key]:
                context.append(f"\n>>> FILE: {rel_path}\n{content}")
            processed_categories.add(key)

    # 3. Catch-all for anything else
    remaining = [k for k in all_files.keys() if k not in processed_categories]
    if remaining:
        context.append("\n### SECTION: UNCLASSIFIED DATA ###")
        for cat in sorted(remaining):
            for rel_path, content in all_files[cat]:
                context.append(f"\n>>> FILE: {rel_path}\n{content}")

    context.append("\n--- END CV KNOWLEDGE BASE ---")
    return "\n".join(context)

def load_persona(persona_name, base_path):
    """
    Loads a specific instruction set (persona) from the personas directory.
    """
    path = os.path.join(base_path, "personas", f"{persona_name}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Persona not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _parse_codex_jsonl(stdout):
    """
    Parses Codex CLI --json output and returns the session id, final text, and usage.
    Codex emits JSONL events; the restore/resume key is the thread_id from thread.started.
    """
    thread_id = None
    messages = []
    usage = None
    events = []

    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        events.append(event)
        event_type = event.get("type")
        if event_type == "thread.started":
            thread_id = event.get("thread_id")
        elif event_type == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                text = item.get("text")
                if text:
                    messages.append(text)
        elif event_type == "turn.completed":
            usage = event.get("usage")

    return {
        "thread_id": thread_id,
        "text": "\n".join(messages).strip(),
        "usage": usage,
        "events": events,
    }

def run_codex_json(cmd, prompt, timeout=1800):
    """Runs a Codex CLI command with stdin prompt and parses the JSONL event stream."""
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=timeout,
    )
    parsed = _parse_codex_jsonl(result.stdout)
    parsed["returncode"] = result.returncode
    parsed["stderr"] = result.stderr
    parsed["stdout"] = result.stdout
    return parsed

def create_codex_context_session(cv_context, jd_text="", model=DEFAULT_CONTEXT_MODEL):
    """
    Loads the source context into a Codex thread and returns its restore/resume key.
    The returned value is the Codex thread_id emitted by `codex exec --json`.
    """
    init_prompt = (
        "# MISSION INITIALIZATION\n"
        "You are the central Resume Generation Engine. I am loading your working memory with the source of truth.\n\n"
        "## SOURCE DOCUMENT: CV DATA\n"
        "```text\n"
        f"{cv_context}\n"
        "```\n"
    )

    if jd_text:
        init_prompt += (
            "\n## SOURCE DOCUMENT: TARGET JOB DESCRIPTION\n"
            "```text\n"
            f"{jd_text}\n"
            "```\n"
        )

    init_prompt += (
        "\n## SYSTEM INSTRUCTION\n"
        "1. Ingest the documents above as durable context for later resumed turns.\n"
        "2. Do not summarize or transform the source documents.\n"
        "3. Reply only with: OK."
    )

    cmd = ["codex", "exec", "--model", model, "--json", "--color", "never", "-"]
    return run_codex_json(cmd, init_prompt)

def resume_codex_session(session_id, prompt, model=DEFAULT_TASK_MODEL):
    """
    Resumes a Codex context session with a new prompt and optional model selection.
    This is the restore-point operation used for personas, questions, and work items.
    """
    cmd = ["codex", "exec", "resume", "--model", model, session_id, "--json", "-"]
    return run_codex_json(cmd, prompt)
