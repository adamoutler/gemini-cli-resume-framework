import os
import glob

files = glob.glob('Agentic_Tasks/Orchestrator/**/*.py', recursive=True)

bad_block = """    except subprocess.TimeoutExpired:
            log('ERROR' if 'log' in globals() else 'print', 'subprocess.TimeoutExpired: Gemini CLI hung.')
            continue
        except Exception as e:"""

bad_block2 = """        except subprocess.TimeoutExpired:
            log('ERROR' if 'log' in globals() else 'print', 'subprocess.TimeoutExpired: Gemini CLI hung.')
            continue
        except Exception as e:"""

bad_block3 = """            except subprocess.TimeoutExpired:
            log('ERROR' if 'log' in globals() else 'print', 'subprocess.TimeoutExpired: Gemini CLI hung.')
            continue
        except Exception as e:"""

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove all the incorrectly injected blocks
    if bad_block in content:
        content = content.replace(bad_block, "    except Exception as e:")
    if bad_block2 in content:
        content = content.replace(bad_block2, "        except Exception as e:")
    if bad_block3 in content:
        content = content.replace(bad_block3, "            except Exception as e:")

    # Now manually insert it only in the main try loops.
    # In resume_orchestrator.py, gemini_client.py, generate_cover_letter_only.py, the try block inside call_gemini
    call_gemini_catch = """        except subprocess.TimeoutExpired:
            log("WARN" if "log" in globals() else "print", f"Gemini API Timeout (Attempt {attempt+1}/{MAX_RETRIES}). Backing off...")
            time.sleep(backoff_times[attempt] if attempt < len(backoff_times) else 600)
            continue
        except Exception as e:"""
    content = content.replace("        except Exception as e:\n            log(\"ERROR\", f\"Execution exception: {e}\")\n            return None", call_gemini_catch + '\n            log("ERROR", f"Execution exception: {e}")\n            return None')
    
    # generate_cover_letter_only.py has `print` instead of log
    content = content.replace("        except Exception as e:\n            print(f\"Error: {e}\")\n            return None", call_gemini_catch.replace("log", "print") + '\n            print(f"Error: {e}")\n            return None')

    with open(filepath, 'w') as f:
        f.write(content)
    
print("Cleanup complete.")
