import os
import sys
import subprocess
import json
import time
import re
from collections import Counter

# Configuration
MODEL = "gemini-3.1-pro-preview"
MAX_RETRIES = 5

def log(step, message):
    # Cleaner output: [STEP] Message
    print(f"[{step.upper()}] {message}")

def call_gemini(system_prompt, user_input):
    full_prompt = f"{system_prompt}\n\n--- INPUT DATA ---\n{user_input}"
    cmd = ["gemini", "--output-format", "text"]
    
    backoff_times = [20, 60, 180, 600]
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(
                cmd, 
                input=full_prompt, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                check=False,
                timeout=1800
            )
            
            # Success path
            if result.returncode == 0 and result.stdout.strip():
                time.sleep(10) # Add delay between requests
                return result.stdout.strip()
            
            # Error handling
            err_msg = result.stderr.lower() if result.stderr else ""
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg or result.returncode != 0:
                if attempt == MAX_RETRIES - 1:
                    break
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600 # 32, 64, 128, 256, 512 seconds
                log("WARN", f"Gemini API Error (Attempt {attempt+1}/{MAX_RETRIES}). Backing off for {wait_time}s... Error: {err_msg[:100]}")
                time.sleep(wait_time)
                log("INFO", "Resuming execution after backoff...")
                continue
            
            # Other errors
            log("ERROR", f"Gemini CLI failed: {result.stderr}")
            return None
            
        except subprocess.TimeoutExpired:
            log("WARN" if "log" in globals() else "print", f"Gemini API Timeout (Attempt {attempt+1}/{MAX_RETRIES}). Backing off...")
            time.sleep(backoff_times[attempt] if attempt < len(backoff_times) else 600)
            continue
        except Exception as e:
            log("ERROR", f"Execution exception: {e}")
            return None
            
    log("FATAL", "Failed to communicate cannot reach server. exceeded 429 threshold. Do not attempt to repeat. Do not continue working on this resume. The artifacts from this run should be considered corrupt and unusable.")
    import sys
    sys.exit(1)

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
