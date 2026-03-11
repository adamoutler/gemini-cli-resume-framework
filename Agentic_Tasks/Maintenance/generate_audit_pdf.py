import os
import glob
import markdown
import re
from playwright.sync_api import sync_playwright

CV_DATA_DIR = "cv-data"
OUTPUT_PDF = "cv-data/resumes/Full_CV_Data_Audit.pdf"

def format_frontmatter(content):
    """
    Detects JSON frontmatter between --- and wraps it in a code block for readability.
    """
    # Pattern to match --- {json} --- at the start of the file
    # DOTALL flag allows . to match newlines
    pattern = re.compile(r'^---\s*\n(\{.*?\})\n---\s*', re.DOTALL)
    
    match = pattern.match(content)
    if match:
        json_content = match.group(1)
        # Remove the original frontmatter
        rest_of_content = content[match.end():]
        
        # Reconstruct with markdown code block
        formatted = f"**Metadata:**\n```json\n{json_content}\n```\n\n---\n\n{rest_of_content}"
        return formatted
    
    return content

def generate_audit_pdf():
    print("Gathering CV Data files...")
    files = sorted(glob.glob(os.path.join(CV_DATA_DIR, "**/*.md"), recursive=True))
    
    full_md = "# Full CV Data Audit\n\nGenerated for verification purposes.\n\n"
    
    for file_path in files:
        rel_path = os.path.relpath(file_path, CV_DATA_DIR)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Formatting
            formatted_content = format_frontmatter(content)
            
            # Append to master doc
            full_md += f"<div style='page-break-before: always;'></div>\n\n"
            full_md += f"# 📄 File: {rel_path}\n\n"
            full_md += formatted_content
            full_md += "\n\n"
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print("Converting to HTML...")
    # Convert to HTML
    html_body = markdown.markdown(full_md, extensions=['extra', 'codehilite', 'toc'])
    
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 10pt; margin: 30px; line-height: 1.4; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 5px; margin-top: 30px; }}
            h2 {{ color: #e67e22; margin-top: 20px; }}
            h3 {{ color: #7f8c8d; }}
            code, pre {{ background-color: #f8f9fa; font-family: 'Consolas', 'Monaco', monospace; font-size: 9pt; }}
            pre {{ padding: 10px; border: 1px solid #ddd; border-radius: 4px; white-space: pre-wrap; }}
            blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; color: #777; }}
            hr {{ border: 0; border-top: 1px solid #eee; margin: 20px 0; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html = "audit_temp.html"
    with open(temp_html, "w", encoding='utf-8') as f:
        f.write(full_html)
        
    print(f"Generating PDF: {OUTPUT_PDF}")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(f"file://{os.path.abspath(temp_html)}")
        page.pdf(path=OUTPUT_PDF, format="Letter", print_background=True, margin={"top":"0.5in","bottom":"0.5in","left":"0.5in","right":"0.5in"})
        browser.close()
        
    if os.path.exists(temp_html):
        os.remove(temp_html)
        
    print("Done.")

if __name__ == "__main__":
    generate_audit_pdf()
