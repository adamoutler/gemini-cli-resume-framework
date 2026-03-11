import os
import sys
import markdown
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter

def md_to_pdf(md_path, temp_pdf_path):
    # 1. Read MD
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 2. Convert to HTML
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
    
    # Wrap in basic styling
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; font-size: 10pt; margin: 20px; }}
            pre {{ background: #f4f4f4; padding: 10px; white-space: pre-wrap; }}
            h1, h2, h3 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>Appended CV Data</h1>
        {html_content}
    </body>
    </html>
    """
    
    temp_html = md_path.replace(".md", ".html")
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    # 3. Print to PDF using Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(f"file://{os.path.abspath(temp_html)}")
        page.pdf(path=temp_pdf_path, format="Letter", print_background=True, margin={"top":"0.5in","bottom":"0.5in","left":"0.5in","right":"0.5in"})
        browser.close()
        
    # Cleanup HTML
    if os.path.exists(temp_html):
        os.remove(temp_html)

def append_pdf(original_pdf, data_pdf, output_pdf):
    merger = PdfWriter()
    
    merger.append(original_pdf)
    merger.append(data_pdf)
    
    merger.write(output_pdf)
    merger.close()
    print(f"Merged PDF saved to: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python append_data_to_pdf.py <original_resume_pdf> <cv_data_md> [output_pdf]")
        sys.exit(1)
        
    original_pdf = sys.argv[1]
    cv_data_md = sys.argv[2]
    output_pdf = sys.argv[3] if len(sys.argv) > 3 else original_pdf
    
    temp_data_pdf = "temp_cv_data.pdf"
    
    print("Generating PDF from CV Data...")
    md_to_pdf(cv_data_md, temp_data_pdf)
    
    print(f"Appending to Resume... Output: {output_pdf}")
    append_pdf(original_pdf, temp_data_pdf, output_pdf)
    
    # Cleanup
    if os.path.exists(temp_data_pdf):
        os.remove(temp_data_pdf)
    print("Done.")
