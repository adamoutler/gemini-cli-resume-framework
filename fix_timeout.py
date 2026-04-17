import os
import glob

files = glob.glob('Agentic_Tasks/Orchestrator/**/*.py', recursive=True)

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    # Replace check=False) with check=False, timeout=120)
    if "encoding='utf-8', check=False)" in content:
        content = content.replace("encoding='utf-8', check=False)", "encoding='utf-8', check=False, timeout=120)")
        modified = True

    if "encoding='utf-8',\n                check=False\n            )" in content:
        content = content.replace("encoding='utf-8',\n                check=False\n            )", "encoding='utf-8',\n                check=False,\n                timeout=120\n            )")
        modified = True
        
    if "encoding='utf-8',\n                check=False)" in content:
        content = content.replace("encoding='utf-8',\n                check=False)", "encoding='utf-8',\n                check=False,\n                timeout=120)")
        modified = True

    if modified:
        # Also make sure we catch subprocess.TimeoutExpired
        if "except Exception as e:" in content and "subprocess.TimeoutExpired" not in content:
            content = content.replace("except Exception as e:", "except subprocess.TimeoutExpired:\n            log('ERROR' if 'log' in globals() else 'print', 'subprocess.TimeoutExpired: Gemini CLI hung.')\n            continue\n        except Exception as e:")
            
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

