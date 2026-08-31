"""Homepage auto-updater with live interactive tool search bar & clean dark responsive theme.

Scans all tool pages in output/pages/ and regenerates index.html
to list every tool with real-time client-side search.
"""

import re
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PAGES_DIR, SITE_NAME, SITE_URL


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
    """Regenerate index.html with live interactive search bar."""
    if not PAGES_DIR.exists():
        return "ERROR: output/pages/ directory not found."
    
    html_files = sorted([
        f for f in PAGES_DIR.glob("*.html")
        if f.stem not in ("index", "404")
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
    
    tool_sections = ""
    for cat in category_order:
        if cat not in tools_by_category:
            continue
        icon = CATEGORY_ICONS.get(cat, "🔧")
        tools = tools_by_category[cat]
        cat_slug = cat.lower().replace(" ", "-")
        
        cards = ""
        for tool in tools:
            cards += f"""            <a href="/{tool['slug']}.html" class="tool-card">
                <div class="card-top">
                    <span class="pill-category">{cat}</span>
                    <span class="card-arrow">↗</span>
                </div>
                <h3>{tool['name']}</h3>
                <p>{tool['description']}</p>
            </a>
"""
        
        tool_sections += f"""
        <section id="{cat_slug}" class="category-section">
            <div class="category-header">
                <h2 class="category-title">{icon} {cat}</h2>
                <span class="category-count">{len(tools)} tools</span>
            </div>
            <div class="tools-grid">
{cards}            </div>
        </section>
"""
    
    year = datetime.now().year
    total_tools = len(html_files)
    
    homepage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_NAME} — Free Online Developer & AI Utilities</title>
    <meta name="description" content="Lightning-fast online tools for developers, designers, and AI creators. Free Markdown editor, JSON formatter, prompt token counter, and {total_tools}+ utilities.">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{SITE_NAME} — Free Online Developer & AI Utilities">
    <meta property="og:description" content="Modern, private developer & AI utilities with zero ads and instant client-side execution.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}">
    <link rel="canonical" href="{SITE_URL}">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='24' fill='%234361ee'/%3E%3Cpath d='M56 12 L24 54 L48 54 L44 88 L76 46 L52 46 Z' fill='%23ffdd00' stroke='%23f59e0b' stroke-width='2'/%3E%3C/svg%3E">
    <link rel="alternate icon" href="/favicon.svg">
    
    <!-- Syne (Headings) + Inter (Body) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #f1f5f9;
            background: #09090b;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Responsive Floating Pill Navbar */
        .nav-wrapper {{
            position: sticky;
            top: 14px;
            z-index: 100;
            padding: 0 16px;
            width: 100%;
        }}
        .site-nav {{
            max-width: 980px;
            margin: 0 auto;
            background: rgba(18, 18, 23, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 100px;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
        }}
        .nav-brand {{
            font-family: 'Syne', sans-serif;
            font-size: 1.2rem;
            font-weight: 800;
            color: #ffffff;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.03em;
            flex-shrink: 0;
        }}
        .nav-brand-dot {{
            width: 8px;
            height: 8px;
            background: #3b82f6;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #3b82f6;
        }}
        .nav-links {{
            display: flex;
            gap: 6px;
            align-items: center;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        .nav-links::-webkit-scrollbar {{ display: none; }}
        .nav-link {{
            font-size: 0.82rem;
            font-weight: 600;
            color: #94a3b8;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 100px;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
        }}

        .container {{
            max-width: 980px;
            margin: 0 auto;
            padding: 24px 16px 80px;
        }}
        
        /* Hero Section */
        header {{
            text-align: center;
            padding: clamp(36px, 8vw, 64px) 12px clamp(28px, 6vw, 40px);
        }}
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(59, 130, 246, 0.1);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.25);
            padding: 5px 14px;
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        header h1 {{
            font-family: 'Syne', sans-serif;
            font-size: clamp(2.2rem, 6vw, 3.6rem);
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.04em;
            color: #ffffff;
            margin-bottom: 16px;
        }}
        header h1 span {{
            color: #60a5fa;
        }}
        header p {{
            font-size: clamp(1rem, 2.5vw, 1.15rem);
            color: #94a3b8;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }}

        /* Search Bar */
        .search-box-wrapper {{
            max-width: 580px;
            margin: 32px auto 0;
            width: 100%;
        }}
        .search-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: #121216;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 100px;
            padding: 6px 18px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }}
        .search-box:focus-within {{
            border-color: #3b82f6;
            background: #16161d;
            box-shadow: 0 0 24px rgba(59, 130, 246, 0.25), 0 0 0 1px #3b82f6;
        }}
        .search-icon {{
            font-size: 1.1rem;
            margin-right: 12px;
            color: #64748b;
        }}
        .search-box input {{
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            padding: 8px 0;
        }}
        .search-box input::placeholder {{
            color: #64748b;
        }}
        .search-shortcut {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #94a3b8;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Empty Search Results Notice */
        #noResults {{
            display: none;
            text-align: center;
            padding: 60px 20px;
            color: #94a3b8;
        }}
        #noResults h3 {{
            font-family: 'Syne', sans-serif;
            font-size: 1.3rem;
            color: #ffffff;
            margin-bottom: 8px;
        }}

        /* Category Section */
        .category-section {{ margin-top: clamp(36px, 6vw, 56px); }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
            padding-bottom: 10px;
        }}
        .category-title {{
            font-family: 'Syne', sans-serif;
            font-size: clamp(1.2rem, 3.5vw, 1.4rem);
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
        }}
        .category-count {{
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* Responsive Cards Grid */
        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
            gap: 16px;
        }}
        .tool-card {{
            background: #121216;
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 16px;
            padding: 22px;
            text-decoration: none;
            color: inherit;
            transition: all 0.25s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }}
        .tool-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(59, 130, 246, 0.4);
            background: #18181f;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(59, 130, 246, 0.2);
        }}
        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .pill-category {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 3px 10px;
            border-radius: 100px;
        }}
        .card-arrow {{
            color: #64748b;
            font-size: 1rem;
            transition: transform 0.2s ease, color 0.2s ease;
        }}
        .tool-card:hover .card-arrow {{
            color: #60a5fa;
            transform: translate(2px, -2px);
        }}
        .tool-card h3 {{
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }}
        .tool-card p {{
            font-size: 0.86rem;
            color: #94a3b8;
            line-height: 1.5;
        }}

        /* Footer */
        footer {{
            margin-top: 72px;
            padding: 36px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
        }}
        .footer-brand {{
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 6px;
        }}
        footer a {{ color: #93c5fd; text-decoration: none; }}
        footer a:hover {{ text-decoration: underline; }}

        @media (max-width: 640px) {{
            .site-nav {{
                padding: 8px 14px;
                border-radius: 12px;
            }}
            .nav-link {{
                padding: 5px 10px;
                font-size: 0.78rem;
            }}
            .container {{
                padding: 16px 12px 60px;
            }}
            .tool-card {{
                padding: 18px;
            }}
            .search-shortcut {{ display: none; }}
        }}
    </style>
</head>
<body>

    <!-- Floating Pill Navbar -->
    <div class="nav-wrapper">
        <nav class="site-nav">
            <a href="/" class="nav-brand">
                <span class="nav-brand-dot"></span>
                {SITE_NAME}
            </a>
            <div class="nav-links">
                <a href="#ai-utilities" class="nav-link">AI</a>
                <a href="#developer-tools" class="nav-link">Developer</a>
                <a href="#text-tools" class="nav-link">Text</a>
                <a href="#design-tools" class="nav-link">Design</a>
            </div>
        </nav>
    </div>

    <div class="container">
        <header>
            <div class="hero-badge">⚡ {total_tools} Free Production Tools</div>
            <h1>The Developer & AI Suite built for <span>speed.</span></h1>
            <p>High-performance web utilities that run 100% inside your browser. No sign-ups, no paywalls, and zero tracking.</p>
            
            <!-- Live Search Bar -->
            <div class="search-box-wrapper">
                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="toolSearch" placeholder="Search {total_tools}+ developer & AI tools... (Press '/' to focus)" autocomplete="off" oninput="filterTools()">
                    <span class="search-shortcut">/</span>
                </div>
            </div>
        </header>

        <!-- No Results Fallback -->
        <div id="noResults">
            <h3>No matching tools found</h3>
            <p>Try searching for terms like <i>json, base64, markdown, token, uuid, or regex</i>.</p>
        </div>

{tool_sections}

        <footer>
            <div class="footer-brand">{SITE_NAME}</div>
            <p>&copy; {year} {SITE_NAME}. Free open utilities for builders.</p>
            <p style="margin-top: 6px; color: #64748b;">All processing happens locally in your browser.</p>
            <div style="margin-top: 14px; display: flex; justify-content: center; gap: 20px; font-size: 0.85rem;">
                <a href="/about.html" style="color: #94a3b8; text-decoration: none;">About</a>
                <a href="/contact.html" style="color: #94a3b8; text-decoration: none;">Contact</a>
                <a href="/privacy.html" style="color: #94a3b8; text-decoration: none;">Privacy Policy</a>
                <a href="/terms.html" style="color: #94a3b8; text-decoration: none;">Terms of Service</a>
            </div>
        </footer>
    </div>

    <!-- Client-Side Instant Search Filter -->
    <script>
        function filterTools() {{
            const q = document.getElementById('toolSearch').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.tool-card');
            const sections = document.querySelectorAll('.category-section');
            let visibleTotal = 0;

            cards.forEach(card => {{
                const title = card.querySelector('h3').textContent.toLowerCase();
                const desc = card.querySelector('p').textContent.toLowerCase();
                const cat = card.querySelector('.pill-category').textContent.toLowerCase();
                const match = title.includes(q) || desc.includes(q) || cat.includes(q);
                card.style.display = match ? 'flex' : 'none';
                if (match) visibleTotal++;
            }});

            sections.forEach(sec => {{
                const visibleCards = sec.querySelectorAll('.tool-card:not([style*="display: none"])');
                sec.style.display = visibleCards.length > 0 ? 'block' : 'none';
            }});

            const emptyState = document.getElementById('noResults');
            if (emptyState) {{
                emptyState.style.display = (visibleTotal === 0 && q !== '') ? 'block' : 'none';
            }}
        }}

        // Shortcut: Press '/' to focus search bar
        document.addEventListener('keydown', e => {{
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {{
                e.preventDefault();
                document.getElementById('toolSearch').focus();
            }}
        }});
    </script>

    <!-- GoatCounter Analytics -->
    <script data-goatcounter="https://aitoolsuite.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>"""
    
    index_path = PAGES_DIR / "index.html"
    index_path.write_text(homepage_html, encoding="utf-8")
    
    return f"SUCCESS: Homepage updated with search bar and {total_tools} tools across {len(tools_by_category)} categories."


if __name__ == "__main__":
    result = update_homepage()
    print(result)
