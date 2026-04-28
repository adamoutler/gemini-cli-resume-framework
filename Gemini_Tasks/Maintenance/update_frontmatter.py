import os
import re

# Read the repository list
with open('PersonalProjects/repos.txt', 'r') as f:
    repo_content = f.read()

# Parse the repository list to get project names
project_names = re.findall(r'^(\S+?) Public', repo_content, re.MULTILINE)

# Get the list of markdown files in the PersonalProjects directory
md_files = [f for f in os.listdir('PersonalProjects') if f.endswith('.md')]

# Create a mapping from project name (lowercase) to markdown file
file_map = {}
for filename in md_files:
    key = filename.replace('-review.md', '').replace('.md', '').lower()
    file_map[key] = filename

# Now iterate through the found project names
for name in project_names:
    lookup_name = name.lower()

    if lookup_name in file_map:
        md_file_path = os.path.join('PersonalProjects', file_map[lookup_name])
        github_url = f"https://github.com/[Username]/{name}"

        with open(md_file_path, 'r') as f:
            content = f.read()

        # Check if frontmatter exists
        if content.startswith('---'):
            parts = content.split('---', 2)
            frontmatter = parts[1]
            body = parts[2]

            if f'github_url: {github_url}' in frontmatter:
                print(f"URL already present in {md_file_path}")
                continue

            if 'github_url:' in frontmatter:
                new_frontmatter = re.sub(r'github_url:.*', f'github_url: {github_url}', frontmatter)
            else:
                new_frontmatter = frontmatter.strip() + f'\ngithub_url: {github_url}\n'
            
            new_content = f'---\n{new_frontmatter.strip()}\n---\n{body}'

        else:
            # No frontmatter, so create it
            new_content = f'---\ngithub_url: {github_url}\n---\n\n{content}'

        with open(md_file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated {md_file_path} with {github_url}")

    else:
        print(f"No matching file found for project: {name}")
