import os
import glob
import re
import yaml

def extract_url_from_text(content):
    # Try to find standard markdown links: [text](url)
    md_links = re.findall(r'\[.*?\]\((https?://[^)]+)\)', content)
    
    # Try to find raw URLs
    raw_urls = re.findall(r'(https?://[^\s\)]+)', content)
    
    all_urls = md_links + raw_urls
    
    if not all_urls:
        return None

    # Priority filtering
    for url in all_urls:
        if "github.com" in url or "git.example.com" in url:
            return url
    for url in all_urls:
        if "thingiverse.com" in url or "youtube.com" in url:
            return url
            
    return all_urls[0]

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split Frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        # print(f"Skipping {file_path}: No valid frontmatter found.")
        return False

    raw_frontmatter = match.group(1)
    body_content = match.group(2)

    try:
        frontmatter = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError:
        print(f"Error parsing YAML in {file_path}")
        return False

    # Check if 'url' already exists
    if 'url' in frontmatter and frontmatter['url']:
        return False # Already has URL, nothing to do

    # Look for alternate keys in frontmatter
    url_keys = ['link', 'project_url', 'article_url', 'repo', 'repository', 'website', 'source_code', 'github_url']
    found_url = None
    
    for key in url_keys:
        if key in frontmatter and frontmatter[key]:
            val = frontmatter[key]
            if isinstance(val, list):
                found_url = val[0]
            else:
                found_url = val
            break
            
    # If not in frontmatter, look in body
    if not found_url:
        found_url = extract_url_from_text(body_content)

    if found_url:
        # Update Frontmatter
        frontmatter['url'] = found_url
        
        # We need to dump it back to string. 
        # yaml.safe_dump will create standard block YAML.
        new_frontmatter_str = yaml.safe_dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
        
        new_content = f"---\n{new_frontmatter_str}\n---\n{body_content}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {os.path.basename(file_path)}: Added url={found_url}")
        return True
    
    return False

def main():
    base_dir = "cv-data"
    dirs_to_scan = ["authored-articles", "personal-projects"]
    
    count = 0
    for subdir in dirs_to_scan:
        search_path = os.path.join(base_dir, subdir, "*.md")
        files = glob.glob(search_path)
        
        for file_path in files:
            if update_file(file_path):
                count += 1

    print(f"Finished. Updated {count} files.")

if __name__ == "__main__":
    main()
