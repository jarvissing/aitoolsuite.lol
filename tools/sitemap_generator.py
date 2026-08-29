"""Sitemap and robots.txt generator for SEO crawling.

Scans all tool pages and generates sitemap.xml and robots.txt.
"""

from pathlib import Path
from datetime import datetime
from config.settings import PAGES_DIR, SITE_URL


def generate_sitemap() -> str:
    """Generate sitemap.xml and robots.txt in output/pages/."""
    if not PAGES_DIR.exists():
        return "ERROR: output/pages/ directory not found."

    html_files = sorted([
        f for f in PAGES_DIR.glob("*.html")
        if f.stem != "404"
    ])

    today = datetime.now().strftime("%Y-%m-%d")

    # Build XML
    urls_xml = []
    
    # Homepage first (highest priority)
    urls_xml.append(f"""    <url>
        <loc>{SITE_URL}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>""")

    # All other tool pages
    for f in html_files:
        if f.stem == "index":
            continue
        urls_xml.append(f"""    <url>
        <loc>{SITE_URL}/{f.name}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls_xml)}
</urlset>
"""

    sitemap_path = PAGES_DIR / "sitemap.xml"
    sitemap_path.write_text(sitemap_content.strip(), encoding="utf-8")

    # Generate robots.txt
    robots_content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    robots_path = PAGES_DIR / "robots.txt"
    robots_path.write_text(robots_content.strip(), encoding="utf-8")

    return f"SUCCESS: Generated sitemap.xml ({len(urls_xml)} URLs) and robots.txt"


if __name__ == "__main__":
    print(generate_sitemap())
