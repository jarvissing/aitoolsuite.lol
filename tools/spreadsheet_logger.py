"""Action logging module to keep track of agent operations."""

import csv
import datetime
from pathlib import Path
from config.settings import LOGS_DIR

def log_action(action_type: str, tool_name: str, keyword: str, url: str, status: str, details: str = "") -> str:
    """
    Logs an action to the action_log.csv file.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "action_log.csv"
    
    file_exists = log_file.exists()
    timestamp = datetime.datetime.now().isoformat()
    
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "action_type", "tool_name", "keyword", "url", "status", "details"])
        writer.writerow([timestamp, action_type, tool_name, keyword, url, status, details])
        
    return f"Action logged: {action_type} - {status}"

def get_daily_summary() -> str:
    """
    Reads today's entries and returns a formatted summary.
    """
    log_file = LOGS_DIR / "action_log.csv"
    if not log_file.exists():
        return "NO_ACTIONS_TODAY"
        
    today = datetime.datetime.now().date().isoformat()
    
    tools_published = 0
    keywords_processed = 0
    errors = 0
    
    has_entries = False
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = row.get("timestamp", "")
                if ts.startswith(today):
                    has_entries = True
                    action = row.get("action_type", "")
                    status = row.get("status", "")
                    
                    if status.lower() == "error" or status.lower() == "failed":
                        errors += 1
                        
                    if action == "publish_tool":
                        tools_published += 1
                    elif action == "process_keyword":
                        keywords_processed += 1
                        
        if not has_entries:
            return "NO_ACTIONS_TODAY"
            
        return f"Daily Summary ({today}):\n- Tools Published: {tools_published}\n- Keywords Processed: {keywords_processed}\n- Errors: {errors}"
    except Exception as e:
        return f"Error reading summary: {str(e)}"

def get_full_log(last_n: int = 50) -> str:
    """
    Returns the last N entries from the action log.
    """
    log_file = LOGS_DIR / "action_log.csv"
    if not log_file.exists():
        return "Log file is empty or does not exist."
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if len(lines) <= 1:
            return "Log file is empty."
            
        header = lines[0]
        data_lines = lines[1:]
        
        last_entries = data_lines[-last_n:]
        
        return header + "".join(last_entries)
    except Exception as e:
        return f"Error reading full log: {str(e)}"
