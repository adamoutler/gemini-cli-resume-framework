import os
import sys
import subprocess
import json
import time
import re
from collections import Counter

# Configuration
MODEL = "gemini-3-pro-preview"
MAX_RETRIES = 5

def log(step, message):
    # Cleaner output: [STEP] Message
    print(f"[{step.upper()}] {message}")

def call_gemini(system_prompt, user_input):
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    cmd = ["gemini", "--output-format", "text"]
    
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(
                cmd, 
                input=full_prompt, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                check=False
            )
            
            # Success path
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # Error handling
            err_msg = result.stderr.lower() if result.stderr else ""
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg or result.returncode != 0:
                wait_time = (2 ** attempt) * 32 # 32, 64, 128, 256, 512 seconds
                log("WARN", f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s... Error: {err_msg[:100]}")
                time.sleep(wait_time)
                log("INFO", "Resuming execution after backoff...")
                continue
            
            # Other errors
            log("ERROR", f"Gemini CLI failed: {result.stderr}")
            return None
            
        except Exception as e:
            log("ERROR", f"Execution exception: {e}")
            return None
            
    log("FATAL", "Max retries exceeded for Gemini API call.")
    return None

def extract_json(text):
    if not text: return None
    import re
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try: return json.loads(match.group(1))
        except: pass
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except: pass
    return None

def calculate_word_frequency(text):
    # Basic stop words to ignore for better keyword highlighting
    stop_words = {
        "the", "and", "to", "of", "a", "in", "is", "that", "for", "it", "as", "was", "with", "on", 
        "are", "be", "this", "an", "at", "by", "not", "or", "from", "but", "we", "you", "can", "will",
        "has", "have", "had", "which", "one", "their", "if", "so", "what", "all", "were", "when", "there",
        "use", "your", "how", "said", "do", "its", "about", "into", "than", "them", "then", "like", "our",
        "two", "more", "these", "want", "way", "look", "first", "also", "new", "because", "day", "more",
        "use", "no", "man", "find", "here", "thing", "give", "many", "well", "up", "out", "who"
    }

    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [w for w in words if w not in stop_words and not w.isdigit() and len(w) > 2]
    
    counter = Counter(filtered_words)
    # Get top 100 most frequent words
    most_common = counter.most_common(100)
    
    freq_list = [{word: count} for word, count in most_common]
    
    return json.dumps({"word_frequency": freq_list}, indent=2)

def save_resume(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return path
