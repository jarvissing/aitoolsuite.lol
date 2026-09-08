"""Homepage auto-updater with live interactive tool search bar & clean dark responsive theme.

Scans all tool pages in output/pages/ and regenerates index.html
to list every tool with real-time client-side search.
"""

import re
from pathlib import Path
from datetime import datetime
import sys
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PAGES_DIR, SITE_NAME, SITE_URL, TEMPLATES_DIR


def extract_tool_info(filepath: Path) -> dict:
    """Extract tool name, description, and category from an HTML page."""
    content = filepath.read_text(encoding="utf-8")
    slug = filepath.stem
    
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.DOTALL)
    tool_name = re.sub(r"<[^>]+>", "", title_match.group(1).strip()) if title_match else slug.replace("-", " ").title()
    
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content)
    description = desc_match.group(1).strip()[:110] if desc_match else ""
    if len(description) == 110:
        description += "..."
    
    category = "Developer Tools"
    if any(word in slug for word in ["word", "case", "lorem", "text", "counter", "markdown"]):
        category = "Text Tools"
    elif any(word in slug for word in ["color", "gradient", "favicon", "image", "svg", "css", "px", "rem"]):
        category = "Design Tools"
    elif any(word in slug for word in ["token", "prompt", "llm", "ai", "cost"]):
        category = "AI Utilities"
    elif any(word in slug for word in ["meta", "robots", "sitemap", "seo", "schema"]):
        category = "SEO Tools"
    
    return {
        "slug": slug,
        "name": tool_name,
        "description": description,
        "category": category,
    }


CATEGORY_ICONS = {
    "AI Utilities": "⚡",
    "Developer Tools": "🛠️",
    "Text Tools": "📝",
    "Design Tools": "🎨",
    "SEO Tools": "🔍",
}


def update_homepage() -> str:
    """Regenerate index.html using Jinja2 homepage_template.html."""
    if not PAGES_DIR.exists():
        return "ERROR: output/pages/ directory not found."
    
    html_files = sorted([
        f for f in PAGES_DIR.glob("*.html")
        if f.stem not in ("index", "404", "privacy", "terms", "about", "contact", "admin-ignore")
    ])
    
    if not html_files:
        return "ERROR: No tool pages found."
    
    tools_by_category = {}
    for f in html_files:
        info = extract_tool_info(f)
        cat = info["category"]
        if cat not in tools_by_category:
            tools_by_category[cat] = []
        tools_by_category[cat].append(info)
    
    category_order = ["AI Utilities", "Developer Tools", "Text Tools", "Design Tools", "SEO Tools"]
    categories = []
    for cat in category_order:
        if cat not in tools_by_category:
            continue
        categories.append({
            "name": cat,
            "slug": cat.lower().replace(" ", "-"),
            "icon": CATEGORY_ICONS.get(cat, "🔧"),
            "tools": tools_by_category[cat]
        })
    
    total_tools = len(html_files)
    
    # Locate templates directory robustly
    templates_dir = TEMPLATES_DIR
    if not (templates_dir / "homepage_template.html").exists():
        if (PAGES_DIR / "templates" / "homepage_template.html").exists():
            templates_dir = PAGES_DIR / "templates"
        elif (PROJECT_ROOT / "templates" / "homepage_template.html").exists():
            templates_dir = PROJECT_ROOT / "templates"
            
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("homepage_template.html")
    homepage_html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        total_tools=total_tools,
        year=datetime.now().year,
        categories=categories
    )
    
    index_path = PAGES_DIR / "index.html"
    index_path.write_text(homepage_html, encoding="utf-8")
    
    return f"SUCCESS: Homepage updated with Jinja2 template and {total_tools} tools across {len(categories)} categories."


if __name__ == "__main__":
    result = update_homepage()
    print(result)
