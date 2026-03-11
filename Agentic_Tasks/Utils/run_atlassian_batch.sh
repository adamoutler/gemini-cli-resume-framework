#!/bin/bash
source venv/bin/activate

run_orchestrator() {
    jd_file="$1"
    echo "Starting Orchestrator for $jd_file"
    python3 Agentic_Tasks/Orchestrator/resume_orchestrator.py --jd "$jd_file"
    echo "Finished $jd_file"
    echo "---------------------------------------------------"
}

run_orchestrator "cv-data/resumes/[Your Name]-Distinguished_Engineer_[Company]_Corporate_Engineering-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Lead_Principal_Technical_Program_Manager-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Principal_Engineer-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Principal_Software_Engineer_FedRAMP-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Backend_Software_Engineer-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Full_Stack_Software_Engineer-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Principal_Engineer_Identity-[Company]-job-description.txt"
run_orchestrator "cv-data/resumes/[Your Name]-Senior_Principal_Software_Engineer-[Company]-job-description.txt"
