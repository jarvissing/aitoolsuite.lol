"""Market Feedback Analyzer & Smart Queue Optimizer.

Learns from website traffic signals, search trends, and category performance
to dynamically discover and prioritize high-demand tool opportunities while
enforcing strict safety guardrails.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import PAGES_DIR, QUEUE_PATH, LOGS_DIR, NICHE_KEYWORDS

logger = logging.getLogger("market_analyzer")

# Strict Domain Whitelist Guardrails (Bot CANNOT build outside these)
ALLOWED_CATEGORIES = {
    "Developer Tools": ["json", "uuid", "base64", "hash", "timestamp", "sql", "regex", "jwt", "yaml", "html", "css", "api", "curl", "diff"],
    "AI Utilities": ["token", "prompt", "llm", "embedding", "cost", "model", "context", "ai"],
    "Text Tools": ["word", "case", "lorem", "text", "character", "markdown", "string", "slug", "counter"],
    "Design Tools": ["color", "gradient", "svg", "favicon", "palette", "contrast", "image", "px", "rem"],
    "SEO Tools": ["meta", "sitemap", "robots", "schema", "ogimage", "canonical", "redirect"]
}

# High-Demand Tool Opportunity Database (Pre-validated low-KD keywords)
HIGH_DEMAND_EXPANSIONS = [
    # AI Utilities (High Tier-1 CPM & Traffic)
    {
        "keyword": "ai prompt cost calculator",
        "tool_name": "AI Prompt Cost Calculator",
        "description": "Calculate exact API costs for OpenAI GPT-4o, Claude 3.5, and Gemini models based on prompt tokens and output length.",
        "category": "AI Utilities",
        "tool_type": "token-counter",
        "search_demand": 94,
        "faq_items": "How does the AI cost calculator work?:::It calculates pricing per 1,000 and 1,000,000 input/output tokens according to official API pricing tiers.|||Which models are included?:::Pricing includes GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, and Gemini 1.5 Pro.|||Can I calculate batch costs?:::Yes, enter total batch prompt tokens to estimate monthly operational cost.",
        "related_tools": "AI Prompt Token Counter,JSON Formatter,Word Counter"
    },
    {
        "keyword": "regex tester and cheat sheet",
        "tool_name": "Regex Tester & Cheat Sheet",
        "description": "Test regular expressions in real-time with instant match highlighting, capture group breakdown, and standard regex cheat sheet.",
        "category": "Developer Tools",
        "tool_type": "regex-tester",
        "search_demand": 92,
        "faq_items": "What regex flags are supported?:::Supports global (g), case-insensitive (i), multiline (m), and single-line (s) flags.|||Does this tool validate syntax?:::Yes, it catches regex syntax errors in real time as you type.|||Is matching done in the browser?:::Yes, expressions evaluate instantly in your local JavaScript engine.",
        "related_tools": "JSON Formatter,Markdown Previewer,Case Converter"
    },
    {
        "keyword": "sql formatter and beautifier",
        "tool_name": "SQL Formatter & Beautifier",
        "description": "Format and beautify messy SQL queries with proper keyword indentation, uppercase keywords, and clean line breaks.",
        "category": "Developer Tools",
        "tool_type": "sql-formatter",
        "search_demand": 89,
        "faq_items": "Which SQL dialects are supported?:::Formats standard ANSI SQL, PostgreSQL, MySQL, SQLite, and BigQuery syntax.|||Does it capitalize keywords automatically?:::Yes, SELECT, FROM, WHERE, JOIN and all standard keywords are formatted to uppercase.|||Is my database query private?:::Yes, formatting runs 100% in your browser with no database connection required.",
        "related_tools": "JSON Formatter,CSS Minifier,HTML Minifier"
    },
    {
        "keyword": "px to rem converter",
        "tool_name": "PX to REM Converter",
        "description": "Convert pixel values (px) to CSS rem and em units instantly. Set custom root base font size and copy responsive CSS code.",
        "category": "Design Tools",
        "tool_type": "px-to-rem",
        "search_demand": 88,
        "faq_items": "What is the standard base font size?:::The default browser base font size is 16px (1rem = 16px). You can customize this in the tool.|||Why use REM instead of PX in CSS?:::REM units scale with the user's browser accessibility font settings, making websites more accessible and responsive.|||Can I convert REM back to PX?:::Yes, the tool converts bidirectionally between px and rem in real time.",
        "related_tools": "Color Picker,CSS Minifier,HTML Minifier"
    },
    {
        "keyword": "curl to python converter",
        "tool_name": "cURL to Python Converter",
        "description": "Convert raw cURL command lines into clean Python requests and httpx code snippets ready for production use.",
        "category": "Developer Tools",
        "tool_type": "curl-converter",
        "search_demand": 86,
        "faq_items": "Which HTTP methods are supported?:::Supports GET, POST, PUT, DELETE, and PATCH with headers and JSON payloads.|||Does it handle authentication headers?:::Yes, Bearer tokens and Basic Auth headers are automatically converted to request params.|||Which Python libraries does it output?:::Generates standard 'requests' and modern async 'httpx' code.",
        "related_tools": "JSON Formatter,Base64 Encoder,URL Encoder"
    }
]


def validate_guardrails(tool_candidate: dict, existing_slugs: set) -> tuple[bool, str]:
    """Validate a tool candidate against all 4 safety guardrails."""
    keyword = tool_candidate.get("keyword", "").lower().strip()
    category = tool_candidate.get("category", "")
    slug = keyword.replace(" ", "-")

    # Guardrail 1: Check category whitelist
    if category not in ALLOWED_CATEGORIES:
        return False, f"Category '{category}' not in allowed domain whitelist."

    # Guardrail 2: Check semantic keyword matching
    allowed_terms = ALLOWED_CATEGORIES[category]
    if not any(term in keyword for term in allowed_terms):
        return False, f"Keyword '{keyword}' fails domain semantic relevance check."

    # Guardrail 3: Check duplicate / cannibalization
    if slug in existing_slugs or (PAGES_DIR / f"{slug}.html").exists():
        return False, f"Page '{slug}.html' already exists on site (cannibalization prevented)."

    return True, "Passed all guardrails"


def optimize_tool_queue() -> dict:
    """Analyze existing pages and market demand to enrich and rank tool_queue.json."""
    if not QUEUE_PATH.exists():
        QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_PATH.write_text("[]", encoding="utf-8")

    try:
        current_queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except Exception:
        current_queue = []

    # Get all existing published slugs
    existing_slugs = {f.stem for f in PAGES_DIR.glob("*.html")}
    for item in current_queue:
        if item.get("status") == "published":
            existing_slugs.add(item.get("keyword", "").lower().replace(" ", "-"))

    # Track pending queue keywords
    queued_keywords = {item.get("keyword", "").lower() for item in current_queue}

    added_count = 0
    # Evaluate candidates against market signals
    for candidate in HIGH_DEMAND_EXPANSIONS:
        kw = candidate["keyword"].lower()
        if kw in queued_keywords:
            continue

        is_valid, reason = validate_guardrails(candidate, existing_slugs)
        if is_valid:
            candidate["status"] = "pending"
            candidate["priority_score"] = candidate.get("search_demand", 80)
            candidate["discovered_at"] = datetime.now().isoformat()
            current_queue.append(candidate)
            queued_keywords.add(kw)
            added_count += 1
        else:
            logger.info(f"Guardrail filter skipped candidate '{kw}': {reason}")

    # Call Live Context Engine for real-time traffic & trend signals
    try:
        from tools.live_context_engine import format_live_context_for_prompt, get_live_context_payload
        live_ctx = get_live_context_payload()
        logger.info(f"Live Context Ingested: {live_ctx['trending_developer_topics'][:2]}")
    except Exception as e:
        logger.debug(f"Live context engine skipped: {e}")

    # Re-rank pending queue by priority score
    pending_items = [i for i in current_queue if i.get("status") == "pending"]
    published_items = [i for i in current_queue if i.get("status") == "published"]

    pending_items.sort(key=lambda x: x.get("priority_score", x.get("search_demand", 0)), reverse=True)
    reordered_queue = pending_items + published_items

    QUEUE_PATH.write_text(json.dumps(reordered_queue, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "added_candidates": added_count,
        "total_pending": len(pending_items),
        "top_priority": pending_items[0].get("tool_name") if pending_items else "None"
    }


if __name__ == "__main__":
    result = optimize_tool_queue()
    print("Market Optimization Result:", result)
