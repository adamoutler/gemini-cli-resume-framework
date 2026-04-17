import os
from unidecode import unidecode

cv_data_dir = 'cv-data'
for root, dirs, files in os.walk(cv_data_dir):
    if 'resumes' in dirs:
        dirs.remove('resumes')
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            ascii_content = unidecode(content)
            if content != ascii_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(ascii_content)
                print(f"Fixed unicode in {filepath}")
print("Unicode fix complete.")
