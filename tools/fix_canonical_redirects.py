"""Script to inject canonical tags and harmonize URLs across all tool pages."""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.homepage_updater import update_homepage
from tools.sitemap_generator import generate_sitemap
from tools.qa_checker import run_full_qa

pages_dir = Path("output/pages")
tool_files = [
    f for f in pages_dir.glob("*.html")
    if f.stem not in ("index", "404", "privacy", "terms", "about", "contact", "admin-ignore")
]

updated_canonical = 0
updated_og = 0

for f in tool_files:
    content = f.read_text(encoding="utf-8")
    slug = f.stem
    canonical_url = f"https://aitoolsuite.lol/{slug}.html"
    modified = False

    # 1. Ensure canonical tag exists
    if "rel=\"canonical\"" not in content and "rel='canonical'" not in content:
        # Insert after <meta name="robots" content="index, follow">
        if '<meta name="robots" content="index, follow">' in content:
            content = content.replace(
                '<meta name="robots" content="index, follow">',
                f'<meta name="robots" content="index, follow">\n    <link rel="canonical" href="{canonical_url}">'
            )
            modified = True
            updated_canonical += 1
        elif '<head>' in content:
            content = content.replace(
                '<head>',
                f'<head>\n    <link rel="canonical" href="{canonical_url}">'
            )
            modified = True
            updated_canonical += 1
    else:
        # Update canonical URL if missing .html
        content = re.sub(
            r'<link\s+rel=[\'"]canonical[\'"]\s+href=[\'"]https://aitoolsuite\.lol/' + re.escape(slug) + r'[\'"]',
            f'<link rel="canonical" href="{canonical_url}"',
            content
        )

    # 2. Update og:url if missing .html
    old_og = f'<meta property="og:url" content="https://aitoolsuite.lol/{slug}">'
    new_og = f'<meta property="og:url" content="{canonical_url}">'
    if old_og in content:
        content = content.replace(old_og, new_og)
        modified = True
        updated_og += 1

    # 3. Update WebApplication schema URL if missing .html
    old_schema_url = f'"url": "https://aitoolsuite.lol/{slug}"'
    new_schema_url = f'"url": "{canonical_url}"'
    if old_schema_url in content:
        content = content.replace(old_schema_url, new_schema_url)
        modified = True

    if modified:
        f.write_text(content, encoding="utf-8")

print(f"Updated {updated_canonical} pages with canonical tags.")
print(f"Updated {updated_og} pages with .html in og:url and schema.")

# Update homepage and sitemap
print(update_homepage())
print(generate_sitemap())

# Run QA
print("\n--- Running QA Verification ---")
print(run_full_qa())
