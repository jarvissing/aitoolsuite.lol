"""Google Search Console integration and URL logging."""

import csv
import datetime
from pathlib import Path
from config.settings import LOGS_DIR

def submit_url(url: str, page_title: str) -> str:
    """
    Logs URL for indexing. Ready for GSC Indexing API integration.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "submitted_urls.csv"
    
    file_exists = log_file.exists()
    
    timestamp = datetime.datetime.now().isoformat()
    
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["url", "page_title", "submitted_at", "indexed"])
        writer.writerow([url, page_title, timestamp, False])
        
    # GSC Indexing API Integration Template:
    # """
    # from google.oauth2 import service_account
    # import googleapiclient.discovery
    # 
    # SCOPES = ["https://www.googleapis.com/auth/indexing"]
    # ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    # 
    # credentials = service_account.Credentials.from_service_account_file(
    #     'path/to/service_account.json', scopes=SCOPES)
    # service = googleapiclient.discovery.build('indexing', 'v3', credentials=credentials)
    # 
    # body = {
    #     "url": url,
    #     "type": "URL_UPDATED"
    # }
    # response = service.urlNotifications().publish(body=body).execute()
    # """
    
    return f"URL logged successfully to {log_file} at {timestamp}"

def get_submission_log() -> str:
    """
    Reads and returns the URL submission log.
    """
    log_file = LOGS_DIR / "submitted_urls.csv"
    if not log_file.exists():
        return "NO_SUBMISSIONS"
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content or content == "url,page_title,submitted_at,indexed":
                return "NO_SUBMISSIONS"
            return content
    except Exception as e:
        return f"Error reading log: {str(e)}"
