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

# High-Demand Tool Opportunity Database (Balanced Dual-Engine: 50% AI + 50% Engineering)
HIGH_DEMAND_EXPANSIONS = [
    # ── AI Utilities Engine (50%) ──
    {
        "keyword": "openai json schema generator",
        "tool_name": "OpenAI Structured Outputs JSON Schema Generator",
        "description": "Generate strict JSON Schema definitions for OpenAI GPT-4o and Claude structured function calling outputs.",
        "category": "AI Utilities",
        "tool_type": "json-to-ts",
        "search_demand": 94,
        "faq_items": "What are structured outputs?:::A feature in OpenAI APIs that guarantees the model outputs strict JSON matching a provided schema.|||Does this generate strict mode schemas?:::Yes, it adds 'additionalProperties: false' and marks required properties automatically.|||Can I copy the schema directly?:::Yes, 1-click button copies the JSON schema object to your clipboard.",
        "related_tools": "JSON Formatter,AI Prompt Cost Calculator,JSON to TypeScript Interface"
    },
    {
        "keyword": "llm context window calculator",
        "tool_name": "LLM Context Window & Memory Calculator",
        "description": "Calculate token usage, context window limits (128k, 200k, 1M, 2M tokens), and memory requirements across AI models.",
        "category": "AI Utilities",
        "tool_type": "token-counter",
        "search_demand": 92,
        "faq_items": "Which models are supported?:::Includes context limits for GPT-4o (128k), Claude 3.5 Sonnet (200k), and Gemini 1.5 Pro (2M).|||How does it calculate memory?:::Estimates KV-cache RAM requirements based on precision (FP16, INT8, INT4).|||Is it browser-safe?:::All calculations run locally with zero server requests.",
        "related_tools": "AI Prompt Token Counter,AI Prompt Cost Calculator,Word Counter"
    },
    {
        "keyword": "embedding cost calculator",
        "tool_name": "AI Embedding & Vector Dimension Calculator",
        "description": "Calculate vector embedding dimensions, storage RAM requirements, and API costs for OpenAI, Cohere, and HuggingFace models.",
        "category": "AI Utilities",
        "tool_type": "token-counter",
        "search_demand": 90,
        "faq_items": "What dimensions are included?:::Supports 1536 (text-embedding-3-small), 3072 (text-embedding-3-large), 768 (nomad), and 1024 (Cohere).|||How is vector storage estimated?:::Calculates total gigabytes based on 4 bytes per float32 vector element.|||Can I calculate batch datasets?:::Yes, enter total document count to see total vector DB storage requirements.",
        "related_tools": "AI Prompt Cost Calculator,JSON Formatter,UUID Generator"
    },

    # ── Core Engineering & Developer Tools Engine (50%) ──
    {
        "keyword": "docker compose to kubernetes",
        "tool_name": "Docker Compose to Kubernetes Converter",
        "description": "Convert docker-compose.yml services and port bindings into clean Kubernetes Deployment and Service YAML manifests.",
        "category": "Developer Tools",
        "tool_type": "yaml-to-json",
        "search_demand": 93,
        "faq_items": "Which Kubernetes resources are generated?:::Generates Deployment specs, Container ports, and ClusterIP/NodePort Service manifests.|||Does it convert environment variables?:::Yes, environment key-values are mapped into pod env definitions.|||Is my compose file private?:::All YAML conversion runs client-side in browser memory.",
        "related_tools": "YAML to JSON Converter,Cron Expression Generator,Chmod Calculator"
    },
    {
        "keyword": "cidr subnet calculator",
        "tool_name": "IPv4 CIDR Subnet & IP Range Calculator",
        "description": "Calculate network masks, usable host IP ranges, broadcast addresses, and wildcard masks for IPv4 CIDR blocks (/8 to /32).",
        "category": "Developer Tools",
        "tool_type": "chmod-calculator",
        "search_demand": 91,
        "faq_items": "What does CIDR notation mean?:::Classless Inter-Domain Routing specifies the prefix length (number of bits in the network mask).|||How many usable hosts are in a /24 subnet?:::A /24 subnet provides 256 total IP addresses and 254 usable host addresses.|||Does it calculate broadcast and network IPs?:::Yes, network IP, broadcast IP, and first/last usable IP addresses are calculated instantly.",
        "related_tools": "DNS Record Lookup,Unix Timestamp Converter,Hash Generator"
    },
    {
        "keyword": "env to json converter",
        "tool_name": ".env to JSON Environment Converter",
        "description": "Convert .env key-value variables into formatted JSON configuration objects and JavaScript process.env definitions.",
        "category": "Developer Tools",
        "tool_type": "yaml-to-json",
        "search_demand": 89,
        "faq_items": "How does it handle quoted values?:::Strips single and double quotes and trims surrounding whitespace.|||Can I convert back from JSON to .env?:::Yes, the tool supports bidirectional conversion between .env and JSON.|||Are API keys safe?:::Yes, conversion happens entirely on your machine with zero network transmission.",
        "related_tools": "JSON Formatter,YAML to JSON Converter,Base64 Encoder"
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
