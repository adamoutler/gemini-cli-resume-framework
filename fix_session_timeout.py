import os

filepath = 'Agentic_Tasks/Orchestrator/utils/session_manager.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the inner try-except block
old_block = """        except Exception as e:
            log(f"Session initialization failed: {e}")
            return None"""

new_block = """        except subprocess.TimeoutExpired:
            log(f"Gemini API Timeout (Attempt {attempt+1}/{MAX_RETRIES}). Backing off...")
            import time
            time.sleep(backoff_times[attempt] if attempt < len(backoff_times) else 600)
            continue
        except Exception as e:
            log(f"Session initialization failed: {e}")
            return None"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Fixed session_manager.py")
else:
    print("Could not find the block in session_manager.py")

