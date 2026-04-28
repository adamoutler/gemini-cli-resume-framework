#!/bin/bash
mkdir -p cv-data/resumes

fetch_and_convert() {
    url="$1"
    outfile="$2"
    echo "Processing $url -> $outfile"
    # User agent to avoid basic blocks, though [Company] might require more.
    curl -s -L -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "$url" | pandoc -f html -t plain > "$outfile"
}

fetch_and_convert "https://www.[company].com/company/careers/details/17053" "cv-data/resumes/[Your Name]-Distinguished_Engineer_[Company]_Corporate_Engineering-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/14923" "cv-data/resumes/[Your Name]-Lead_Principal_Technical_Program_Manager-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/20516" "cv-data/resumes/[Your Name]-Senior_Principal_Engineer-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/17551" "cv-data/resumes/[Your Name]-Senior_Principal_Software_Engineer_FedRAMP-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/23642" "cv-data/resumes/[Your Name]-Senior_Backend_Software_Engineer-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/23644" "cv-data/resumes/[Your Name]-Senior_Full_Stack_Software_Engineer-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/8233" "cv-data/resumes/[Your Name]-Senior_Principal_Engineer_Identity-[Company]-job-description.txt"
fetch_and_convert "https://www.[company].com/company/careers/details/20684" "cv-data/resumes/[Your Name]-Senior_Principal_Software_Engineer-[Company]-job-description.txt"

ls -l cv-data/resumes/*[Company]-job-description.txt
