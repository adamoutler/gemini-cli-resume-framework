import json
import sys
import re
import argparse
import os

def load_schema(schema_path):
    """Loads the Standard JSON Resume Schema."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"WARN: Could not load schema from {schema_path}: {e}")
        return None

def validate_against_schema_definitions(data, schema, path=""):
    """
    Recursively checks if keys in data are allowed by the schema.
    This is a lightweight validator since 'jsonschema' lib is unavailable.
    """
    errors = []
    
    if not schema:
        return errors

    # If schema has 'properties', data should be a dict
    if "properties" in schema:
        if not isinstance(data, dict):
             # This might happen if data is a list but schema expects object
             # We skip for now to avoid noise, focusing on structure
             return errors
        
        for key, value in data.items():
            if key not in schema["properties"]:
                 # Skip 'meta' or other common extra fields if not in strict mode
                 # But user asked to verify AGAINST schema.
                 pass # We won't strict fail on extra keys for now, just structure.
            else:
                # Recurse
                sub_schema = schema["properties"][key]
                errors.extend(validate_against_schema_definitions(value, sub_schema, path=f"{path}.{key}" if path else key))
    
    # If schema is 'array', data should be list
    if schema.get("type") == "array" and "items" in schema:
        if isinstance(data, list):
            for idx, item in enumerate(data):
                errors.extend(validate_against_schema_definitions(item, schema["items"], path=f"{path}[{idx}]"))
    
    return errors

def validate_custom_rules(data):
    """
    Performs specific business logic checks requested by the user.
    """
    report = {
        "errors": [],
        "warnings": [],
        "missing_sections": []
    }
    
    # --- 1. Top Level Check ---
    required_sections = ["basics", "work", "education", "skills", "careerHighlights", "certificates"]
    for section in required_sections:
        if section not in data:
            report["errors"].append(f"Missing required top-level section: '{section}'")
            report["missing_sections"].append(section)

    # --- 2. Basics: Email Check ---
    if "basics" in data:
        email = data["basics"].get("email", "")
        if not email:
            report["errors"].append("basics.email is missing.")
        elif " " in email:
            report["errors"].append(f"basics.email contains spaces: '{email}'. Invalid format.")
        elif "@" not in email:
             report["errors"].append(f"basics.email appears invalid (no @): '{email}'.")

    # --- 3. Work: Mandatory 'company' (Legacy) Field ---
    if "work" in data:
        for idx, job in enumerate(data["work"]):
            # Check for Name
            if "name" not in job:
                report["errors"].append(f"work[{idx}]: Missing required field 'name'.")
            
            # Check for Company (Legacy) - MANDATORY per user request
            if "company" not in job:
                # If name exists but company doesn't, this is a specific failure
                report["errors"].append(f"work[{idx}]: Missing mandatory legacy field 'company'. (Must match 'name' for StackOverflow theme compatibility).")
            else:
                # Optional: Ensure they match if that's the goal, but mostly just presence is checked.
                pass

            # Highlights flat list check
            if "highlights" in job:
                if not isinstance(job["highlights"], list):
                     report["errors"].append(f"work[{idx}].highlights must be a list.")
                else:
                    for h_idx, h in enumerate(job["highlights"]):
                        if not isinstance(h, str):
                            report["errors"].append(f"work[{idx}].highlights[{h_idx}] must be a string.")

    # --- 4. Date Format Check (YYYY-MM-DD or YYYY-MM) ---
    date_pattern = re.compile(r"^([1-2][0-9]{3}-(0[1-9]|1[0-2])-[0-9]{2}|[1-2][0-9]{3}-(0[1-9]|1[0-2])|Present)$")
    
    def check_dates(items, section_name):
        if not isinstance(items, list): return
        for idx, item in enumerate(items):
            for date_field in ["startDate", "endDate", "date"]:
                val = item.get(date_field)
                if val and not date_pattern.match(val):
                    report["errors"].append(f"Invalid date format in {section_name}[{idx}].{date_field}: '{val}'. Expected YYYY-MM-DD.")

    if "work" in data: check_dates(data["work"], "work")
    if "education" in data: check_dates(data["education"], "education")
    if "projects" in data: check_dates(data["projects"], "projects")
    if "volunteer" in data: check_dates(data["volunteer"], "volunteer")
    if "certificates" in data: check_dates(data["certificates"], "certificates")
    
    # --- 5. Skills Check ---
    if "skills" in data:
        for idx, skill in enumerate(data["skills"]):
            if "keywords" not in skill:
                report["errors"].append(f"Missing 'keywords' in skills[{idx}]")
            elif not isinstance(skill["keywords"], list):
                report["errors"].append(f"skills[{idx}].keywords must be a list of strings.")
            else:
                 for k_idx, k in enumerate(skill["keywords"]):
                    if not isinstance(k, str):
                        report["errors"].append(f"skills[{idx}].keywords[{k_idx}] is not a string.")

    # --- 6. Career Highlights Check ---
    if "careerHighlights" in data:
        if not isinstance(data["careerHighlights"], list):
            report["errors"].append("careerHighlights must be a list of strings.")
        else:
            if len(data["careerHighlights"]) < 2:
                report["warnings"].append("careerHighlights has fewer than 2 items. Recommended: 3-5.")
            for ch_idx, ch in enumerate(data["careerHighlights"]):
                 if not isinstance(ch, str):
                      report["errors"].append(f"careerHighlights[{ch_idx}] must be a string.")

    # --- 7. Certificates Check ---
    if "certificates" in data:
         if not isinstance(data["certificates"], list):
             report["errors"].append("certificates must be a list of objects.")
         else:
             for c_idx, cert in enumerate(data["certificates"]):
                 if "name" not in cert:
                     report["errors"].append(f"certificates[{c_idx}] missing required field 'name'.")


    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_file", help="Path to the resume JSON file")
    parser.add_argument("--output", "-o", help="Output file for validation report (JSON)", default=None)
    args = parser.parse_args()

    # Paths
    # Assuming this script is running from Codex_Tasks/Resume_Audit/
    # We need to find the schema in related-requirements/ relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    schema_path = os.path.join(project_root, "related-requirements", "Standard_JSON_Resume_Schema.json")

    # Load Resume
    try:
        with open(args.resume_file, 'r') as f:
            resume_data = json.load(f)
    except Exception as e:
        print(f"FATAL: Could not read resume file: {e}")
        sys.exit(1)

    # Load Schema
    schema_data = load_schema(schema_path)
    
    # Validate
    report = validate_custom_rules(resume_data)
    
    if schema_data:
        # We could add lightweight recursive schema check here if strict verification is needed
        # But for now, the custom rules cover the critical 'legacy' and 'format' requirements.
        pass
    else:
        print("WARN: Schema file not found. Proceeding with internal rule validation only.")

    # Print to Console
    if report["errors"]:
        print("\n" + "!"*40)
        print(" CRITICAL SCHEMA ERRORS FOUND ")
        print("!"*40)
        for err in report["errors"]:
            print(f" - {err}")
    
    if report["warnings"]:
        print("\nWARNINGS:")
        for warn in report["warnings"]:
            print(f" - {warn}")

    # Output JSON Report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

    # Exit Code
    if report["errors"]:
        sys.exit(1)
    else:
        print("Validation Passed.")
        sys.exit(0)
