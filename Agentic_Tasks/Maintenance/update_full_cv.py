import os
import sys

# Add Orchestrator to path for context_loader
ORCHESTRATOR_DIR = os.path.join(os.getcwd(), "Agentic_Tasks", "Orchestrator")
sys.path.append(ORCHESTRATOR_DIR)

from utils.context_loader import load_cv_context

PROJECT_ROOT = os.getcwd()
CV_DATA_DIR = os.path.join(PROJECT_ROOT, "cv-data")
FULL_CV_PATH = os.path.join(PROJECT_ROOT, "cv-data", "resumes", "full_cv_data_latest.md")

def main():
    print(f"Aggregating CV data from {CV_DATA_DIR}...")
    context = load_cv_context(CV_DATA_DIR)
    
    with open(FULL_CV_PATH, 'w', encoding='utf-8') as f:
        f.write(context)
    
    print(f"Success! Updated {FULL_CV_PATH}")

if __name__ == "__main__":
    main()
