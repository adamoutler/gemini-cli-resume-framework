import subprocess
import re

def detect_widows_and_orphans(pdf_path):
    cmd = ["pdftotext", "-layout", pdf_path, "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    lines = result.stdout.splitlines()
    candidates = []
    
    for i in range(len(lines) - 1):
        current_line = lines[i]
        next_line = lines[i+1]
        
        # Strip trailing whitespace but keep leading to check indentation
        curr_stripped_right = current_line.rstrip()
        next_stripped_right = next_line.rstrip()
        next_stripped_both = next_line.strip()
        
        # A wrapped line candidate usually happens when the current line is long
        # and the next line is short (a widow/orphan) and has similar indentation
        if len(curr_stripped_right) > 75 and 0 < len(next_stripped_both) < 40:
            # Check indentation. In pdftotext -layout, wrapped lines usually 
            # share the exact same indentation or are slightly indented.
            curr_indent = len(current_line) - len(current_line.lstrip())
            next_indent = len(next_line) - len(next_line.lstrip())
            
            # If it looks like a continuation
            if abs(curr_indent - next_indent) < 5:
                # We found a candidate. Combine them to find the original string.
                combined = f"{curr_stripped_right.strip()} {next_stripped_both}"
                # Clean up multiple spaces
                combined = re.sub(r'\s+', ' ', combined)
                candidates.append({
                    "original_text": combined,
                    "overflow_text": next_stripped_both,
                    "chars_to_save": len(next_stripped_both) + 2 # +2 for safety margin
                })
                
    return candidates

if __name__ == "__main__":
    import sys
    res = detect_widows_and_orphans(sys.argv[1])
    for r in res:
        print(f"FOUND: '{r['original_text']}'")
        print(f"  -> Wraps by: '{r['overflow_text']}' ({r['chars_to_save']} chars to save)\n")
