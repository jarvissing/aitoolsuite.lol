"""Daily autonomous publishing runner.

Picks the next approved pending tool from config/tool_queue.json,
generates the SEO page, updates the homepage, generates the sitemap,
runs QA validation, and automatically deploys to GitHub.

Usage:
    py tools/daily_publisher.py
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PAGES_DIR, QUEUE_PATH, LOGS_DIR, SITE_URL
from tools.site_publisher import build_tool_page
from tools.homepage_updater import update_homepage
from tools.sitemap_generator import generate_sitemap
from tools.qa_checker import run_full_qa
from tools.spreadsheet_logger import log_action
from tools.market_analyzer import optimize_tool_queue, auto_replenish_queue

# Set up daily bot logger
LOGS_DIR.mkdir(parents=True, exist_ok=True)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "daily_bot.log", mode="a", encoding="utf-8"),
    ]
)
logger = logging.getLogger("daily_publisher")


def publish_next_tool() -> dict:
    """Publish the next pending tool from the queue with autonomous auto-replenishment."""
    # Step 1: Run Market Feedback Analyzer & Ensure Queue is Replenished
    logger.info("Running Market Feedback Analyzer & Autonomous Replenisher...")
    try:
        rep_res = auto_replenish_queue(min_tools=5)
        logger.info(f"Queue Status / Replenishment: {rep_res}")
    except Exception as e:
        logger.warning(f"Replenishment note: {e}")
    if not QUEUE_PATH.exists():
        logger.error(f"Queue file not found at {QUEUE_PATH}")
        return {"status": "error", "message": "Queue file not found"}

    try:
        queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to read queue: {e}")
        return {"status": "error", "message": str(e)}

    # Find first pending tool
    pending_tool = None
    for item in queue:
        if item.get("status") == "pending":
            pending_tool = item
            break

    if not pending_tool:
        logger.info("No pending tools found! Forcing immediate replenishment...")
        try:
            auto_replenish_queue(min_tools=5)
            queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
            for item in queue:
                if item.get("status") == "pending":
                    pending_tool = item
                    break
        except Exception as e:
            logger.error(f"Forced replenishment error: {e}")

    if not pending_tool:
        logger.error("Failed to acquire pending tool even after replenishment.")
        return {"status": "empty", "message": "No pending tools in queue"}

    keyword = pending_tool.get("keyword")
    tool_name = pending_tool.get("tool_name")
    description = pending_tool.get("description")
    category = pending_tool.get("category", "Developer Tools")
    tool_type = pending_tool.get("tool_type", "")
    faq_items = pending_tool.get("faq_items", "")
    related_tools = pending_tool.get("related_tools", "")

    logger.info(f"🚀 Publishing tool: '{tool_name}' for keyword '{keyword}'...")

    # Build the page
    result = build_tool_page(
        keyword=keyword,
        tool_name=tool_name,
        description=description,
        category=category,
        faq_items=faq_items,
        related_tools=related_tools,
        tool_type=tool_type,
    )
    logger.info(result)

    # Mark as published in queue
    pending_tool["status"] = "published"
    pending_tool["published_at"] = datetime.now().isoformat()
    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")

    # Update Homepage & Sitemap
    logger.info("Updating homepage and generating sitemap...")
    hp_res = update_homepage()
    logger.info(hp_res)
    sm_res = generate_sitemap()
    logger.info(sm_res)

    # Run QA
    logger.info("Running QA verification checks...")
    qa_report = run_full_qa()
    logger.info(f"QA Result:\n{qa_report}")

    # Deploy to GitHub
    if "ALL PAGES PASS QA" in qa_report:
        if os.getenv("GITHUB_ACTIONS"):
            logger.info("Running in GitHub Actions — commit and push will be finalized by workflow runner.")
        else:
            logger.info("Deploying changes to GitHub Pages locally...")
            try:
                pages_dir = str(PAGES_DIR)
                subprocess.run(["git", "add", "."], cwd=pages_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Auto-publish tool: {tool_name}"], cwd=pages_dir, check=True)
                subprocess.run(["git", "push"], cwd=pages_dir, check=True)
                logger.info(f"✅ Successfully deployed '{tool_name}' to {SITE_URL}")
            except Exception as e:
                logger.warning(f"Git push note: {e}")
    else:
        logger.warning("QA check had warnings; review QA report.")

    # Record action
    slug = keyword.lower().replace(" ", "-")
    page_url = f"{SITE_URL}/{slug}.html"
    log_action(
        action_type="PUBLISH",
        tool_name=tool_name,
        keyword=keyword,
        url=page_url,
        status="SUCCESS",
        details=f"Published {tool_name}"
    )

    return {
        "status": "success",
        "tool_name": tool_name,
        "keyword": keyword,
        "url": page_url
    }


if __name__ == "__main__":
    count = 1
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
    
    results = []
    for i in range(count):
        res = publish_next_tool()
        results.append(res)
        print(f"\nTool {i+1} Result: {res}")
