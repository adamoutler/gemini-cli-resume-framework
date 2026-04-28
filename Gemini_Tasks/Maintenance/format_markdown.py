import os
import re

CV_DATA_DIR = "cv-data"

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return False

    if not lines:
        return False

    original_content = "".join(lines)
    new_lines = []
    
    # Regex for list items (unordered: -, *, +; ordered: 1., 2.)
    # Matches: Start of line, optional whitespace (0-3 spaces usually for top level, more for nested), 
    # bullet/number, whitespace.
    # We treat anything looking like a list item as one.
    list_pattern = re.compile(r'^(\s*)([-*+]|\d+\.)\s+')

    for i, line in enumerate(lines):
        # We need to handle the content without the newline for checking
        content_stripped = line.rstrip('\r\n')
        
        is_list_item = list_pattern.match(content_stripped)
        
        if is_list_item:
            # Check previous line in 'new_lines'
            if new_lines:
                prev_line = new_lines[-1]
                prev_content_stripped = prev_line.rstrip('\r\n')
                
                # If previous line is empty (just newline), we are good.
                if prev_content_stripped.strip() == "":
                    pass
                else:
                    # Previous line has text. Is it a list item?
                    prev_is_list = list_pattern.match(prev_content_stripped)
                    
                    if not prev_is_list:
                        # Previous line is NOT a list item (and not empty).
                        # We found a list starting immediately after text.
                        # Insert a newline.
                        new_lines.append('\n')
        
        new_lines.append(line)

    # Ensure trailing newline
    if new_lines:
        last_line = new_lines[-1]
        if not last_line.endswith('\n'):
            new_lines[-1] = last_line + '\n'
        elif last_line != '\n' and not last_line.endswith('\n'): 
            # Case where it might be just text? handled above.
            # But what if the file ends with multiple newlines? 
            # User just said "ends with a newline". One is enough.
            pass
            
    output_content = "".join(new_lines)
    
    if output_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk(CV_DATA_DIR):
        for file in files:
            if file.endswith(".md"):
                if fix_file(os.path.join(root, file)):
                    count += 1
    print(f"Finished. Modified {count} files.")

if __name__ == "__main__":
    main()
