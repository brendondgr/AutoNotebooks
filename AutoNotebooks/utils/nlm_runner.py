import subprocess
import re
import json
import os
import time
from datetime import datetime

def run_nlm(args: list[str], timeout: int = 300, log_key: str = None) -> str:
    cmd = ["uv", "run", "nlm"] + args
    
    log_dir = "logs"
    if log_key:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{safe_filename(log_key)}.log")
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().isoformat()}] RUNNING: {' '.join(cmd)}\n")
    else:
        log_file = None

    output = ""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()
        error_output = result.stderr.strip()
        
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"EXIT CODE: {result.returncode}\n")
                if output:
                    f.write(f"STDOUT:\n{output}\n")
                if error_output:
                    f.write(f"STDERR:\n{error_output}\n")
        
        # If there's an error and stdout is empty, return stderr just in case it's needed
        if result.returncode != 0 and not output:
             output = error_output
    except subprocess.TimeoutExpired as e:
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"TIMEOUT EXPIRED after {timeout} seconds\n")
        output = ""
    except Exception as e:
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"EXCEPTION: {str(e)}\n")
        output = ""
        
    time.sleep(5)
    return output

def extract_notebook_id(output: str) -> str:
    match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', output, re.IGNORECASE)
    return match.group(0) if match else ""

def extract_task_id(output: str) -> str:
    match = re.search(r'task[_\s]*(?:id)?[:\s]*([0-9a-fA-F-]+)', output, re.IGNORECASE)
    if match: return match.group(1).strip()
    match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', output, re.IGNORECASE)
    return match.group(0) if match else ""

def parse_latest_artifacts(out: str) -> dict:
    try:
        raw = json.loads(out or "[]")
        latest: dict = {}
        # Studio status JSON is usually a list of dicts with "type" and "status"
        # We take the last one for each type
        for a in raw:
            latest[a["type"]] = a
        return latest
    except Exception:
        return {}

def safe_filename(key: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', key).lower()
