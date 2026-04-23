import sys
import time

from utils.context_loader import (
    DEFAULT_CONTEXT_MODEL,
    create_codex_context_session,
)

MODEL = DEFAULT_CONTEXT_MODEL

def log(message):
    print(f"[SESSION_MANAGER] {message}", flush=True)

def init_master_session(cv_context, jd_text, model=MODEL):
    """Initializes a Codex context session and returns its thread_id restore key."""
    log(f"Initializing Codex context session with {model}...")

    backoff_times = [20, 60, 180, 600]
    max_retries = 5

    for attempt in range(max_retries):
        try:
            response = create_codex_context_session(cv_context, jd_text, model=model)

            if response["returncode"] == 0 and response.get("thread_id"):
                thread_id = response["thread_id"]
                usage = response.get("usage") or {}
                token_summary = ""
                if usage:
                    token_summary = (
                        f" input_tokens={usage.get('input_tokens')},"
                        f" cached_input_tokens={usage.get('cached_input_tokens')},"
                        f" output_tokens={usage.get('output_tokens')}"
                    )
                log(f"Context restore point ready: {thread_id}{token_summary}")
                return thread_id

            err_msg = (response.get("stderr") or response.get("stdout") or "").lower()
            if "429" in err_msg or "resource" in err_msg or "exhausted" in err_msg:
                if attempt == max_retries - 1:
                    break
                wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
                log(f"Codex API Error (Attempt {attempt+1}/{max_retries}). Backing off for {wait_time}s...")
                time.sleep(wait_time)
                continue

            log(
                "Context session initialization failed. "
                f"returncode={response.get('returncode')} stderr={response.get('stderr')}"
            )
            return None

        except TimeoutError:
            if attempt == max_retries - 1:
                break
            wait_time = backoff_times[attempt] if attempt < len(backoff_times) else 600
            log(f"Codex API Timeout (Attempt {attempt+1}/{max_retries}). Backing off for {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            log(f"Session initialization failed: {e}")
            return None

    log("Failed to initialize Codex context session after retry limit.")
    sys.exit(1)

def fork_session(master_id):
    """
    Returns the Codex restore key for compatibility with older orchestrator code.

    Codex CLI restore points are resumed by thread_id, so there is no session file to
    duplicate. Callers can pass this id to `codex exec resume --model ... <id> -`.
    """
    return master_id
