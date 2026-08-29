"""Settings and configuration for Boring Tool Empire."""

import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# API Keys & External Services
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
DATAFORSEO_LOGIN: str = os.getenv("DATAFORSEO_LOGIN", "")
DATAFORSEO_PASSWORD: str = os.getenv("DATAFORSEO_PASSWORD", "")
GSC_CREDENTIALS_PATH: str = os.getenv("GSC_CREDENTIALS_PATH", "")
GSC_SITE_URL: str = os.getenv("GSC_SITE_URL", "")
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

# Site Configuration
SITE_NAME: str = os.getenv("SITE_NAME", "AI Tool Suite")
SITE_URL: str = os.getenv("SITE_URL", "https://aitoolsuite.lol")

# Directories and File Paths
if (PROJECT_ROOT / "output" / "pages").exists() and not (PROJECT_ROOT / "index.html").exists():
    OUTPUT_DIR: Path = PROJECT_ROOT / "output"
    PAGES_DIR: Path = OUTPUT_DIR / "pages"
    LOGS_DIR: Path = OUTPUT_DIR / "logs"
else:
    OUTPUT_DIR: Path = PROJECT_ROOT
    PAGES_DIR: Path = PROJECT_ROOT
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

TEMPLATES_DIR: Path = PROJECT_ROOT / "templates"
QUEUE_PATH: Path = PROJECT_ROOT / "config" / "tool_queue.json"
PERSISTENCE_DIR: Path = PROJECT_ROOT / ".agent_state"

# Ensure runtime directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
PERSISTENCE_DIR.mkdir(parents=True, exist_ok=True)

# Niche & Keyword Discovery Settings
NICHE: str = "AI / Tech Tools"

NICHE_KEYWORDS: List[str] = [
    "ai image generator",
    "llm comparison tool",
    "token counter",
    "prompt template generator",
    "ai detector",
    "embedding visualizer",
    "json formatter",
    "api tester",
    "regex tester",
    "jwt decoder",
    "uuid generator",
    "base64 encoder",
    "hash generator",
    "qr code generator",
    "color picker",
    "gradient generator",
    "favicon generator",
    "ogimage generator",
    "markdown previewer",
    "diff checker",
    "csv to json",
    "yaml formatter",
    "cron expression generator",
    "sql formatter",
    "html minifier",
    "css minifier",
    "javascript minifier",
    "url encoder",
    "timestamp converter",
    "ip lookup",
    "dns lookup",
    "subdomain finder",
    "curl to fetch converter",
    "svg optimizer",
    "lorem ipsum generator",
    "password generator",
    "chmod calculator",
    "html entity encoder",
    "meta tag generator",
    "robots txt generator",
]

# Tool Categories
TOOL_CATEGORIES: Dict[str, str] = {
    "ai-tools": "AI & Machine Learning",
    "dev-tools": "Developer Utilities",
    "formatters": "Formatters & Converters",
    "web-tools": "Web & Design Utilities",
    "text-tools": "Text & Content Tools",
    "security-tools": "Security & Cryptography",
    "network-tools": "Network & DNS Utilities",
}

# SEO / Keyword Filtering Criteria
KEYWORD_FILTERS: Dict[str, Any] = {
    "max_kd": 35,          # Maximum keyword difficulty (0-100)
    "min_volume": 500,     # Minimum monthly search volume
    "min_cpc": 0.30,       # Minimum cost-per-click ($ USD)
}

# Automation Scheduling Settings
DAILY_TRIGGER_SECONDS: int = 86400
MAX_TOOLS_PER_DAY: int = 1
