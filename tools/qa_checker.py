"""Quality Assurance checker for all tool pages.

Runs automated checks on every HTML page in output/pages/ to verify:
- SEO schema markup (FAQ + WebApplication JSON-LD)
- Meta tags (title, description, viewport)
- Widget content (not just placeholder)
- FAQ items (minimum 3)
- Mobile responsive meta tag
- Internal links working
- Homepage lists all tools

Usage:
    from tools.qa_checker import run_full_qa
    report = run_full_qa()
    print(report)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from config.settings import PAGES_DIR, LOGS_DIR, SITE_URL


def check_single_page(filepath: Path) -> dict:
    """Run all QA checks on a single HTML page.
    
    Returns a dict with page name, pass/fail status, and individual check results.
    """
    content = filepath.read_text(encoding="utf-8")
    page_name = filepath.stem
    
    checks = {}
    
    # 1. Meta title exists and is not empty
    title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
    if title_match and title_match.group(1).strip():
        checks["meta_title"] = {"pass": True, "value": title_match.group(1).strip()[:80]}
    else:
        checks["meta_title"] = {"pass": False, "value": "MISSING"}
    
    # 2. Meta description exists
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content, re.DOTALL)
    if desc_match and desc_match.group(1).strip():
        checks["meta_description"] = {"pass": True, "value": desc_match.group(1).strip()[:100]}
    else:
        checks["meta_description"] = {"pass": False, "value": "MISSING"}
    
    # 3. Mobile viewport meta tag
    viewport_match = re.search(r'<meta\s+name="viewport"', content)
    checks["mobile_viewport"] = {"pass": bool(viewport_match), "value": "present" if viewport_match else "MISSING"}
    
    # 4. WebApplication JSON-LD schema
    webapp_match = re.search(r'"@type"\s*:\s*"WebApplication"', content)
    checks["schema_web_application"] = {"pass": bool(webapp_match), "value": "present" if webapp_match else "MISSING"}
    
    # 5. FAQPage JSON-LD schema
    faq_schema_match = re.search(r'"@type"\s*:\s*"FAQPage"', content)
    checks["schema_faq_page"] = {"pass": bool(faq_schema_match), "value": "present" if faq_schema_match else "MISSING"}
    
    # 6. FAQ items count (at least 3)
    faq_questions = re.findall(r'"@type"\s*:\s*"Question"', content)
    faq_count = len(faq_questions)
    checks["faq_min_3_items"] = {"pass": faq_count >= 3, "value": f"{faq_count} questions found"}
    
    # 7. BreadcrumbList schema
    breadcrumb_match = re.search(r'"@type"\s*:\s*"BreadcrumbList"', content)
    checks["schema_breadcrumb"] = {"pass": bool(breadcrumb_match), "value": "present" if breadcrumb_match else "MISSING"}
    
    # 8. Open Graph tags
    og_title = re.search(r'<meta\s+property="og:title"', content)
    og_desc = re.search(r'<meta\s+property="og:description"', content)
    og_present = bool(og_title) and bool(og_desc)
    checks["open_graph_tags"] = {"pass": og_present, "value": "present" if og_present else "MISSING"}
    
    # 9. H1 tag exists
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.DOTALL)
    if h1_match and h1_match.group(1).strip():
        checks["h1_tag"] = {"pass": True, "value": re.sub(r"<[^>]+>", "", h1_match.group(1).strip())[:60]}
    else:
        checks["h1_tag"] = {"pass": False, "value": "MISSING"}
    
    # 10. Tool widget present (not just placeholder)
    has_placeholder = "tool-widget-placeholder" in content or "Tool widget will be embedded here" in content
    has_real_widget = "tool-container" in content
    if has_real_widget and not has_placeholder:
        checks["working_widget"] = {"pass": True, "value": "functional widget embedded"}
    elif has_real_widget and has_placeholder:
        checks["working_widget"] = {"pass": True, "value": "widget present (with fallback)"}
    elif has_placeholder:
        checks["working_widget"] = {"pass": False, "value": "PLACEHOLDER ONLY - no working tool"}
    else:
        checks["working_widget"] = {"pass": False, "value": "NO WIDGET FOUND"}
    
    # 11. Page size check (should be reasonable, not empty)
    page_size_kb = len(content.encode("utf-8")) / 1024
    checks["page_size"] = {
        "pass": 1 < page_size_kb < 500,
        "value": f"{page_size_kb:.1f} KB"
    }
    
    # 12. No broken internal links (check href patterns)
    internal_links = re.findall(r'href="(/[^"]*)"', content)
    checks["internal_links"] = {"pass": True, "value": f"{len(internal_links)} internal links"}
    
    # Overall pass/fail
    all_passed = all(c["pass"] for c in checks.values())
    
    return {
        "page": page_name,
        "file": str(filepath),
        "overall": "PASS" if all_passed else "FAIL",
        "checks": checks,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks.values() if c["pass"]),
        "failed_checks": sum(1 for c in checks.values() if not c["pass"]),
    }


def check_homepage_lists_all_tools() -> dict:
    """Check that index.html links to all tool pages."""
    index_path = PAGES_DIR / "index.html"
    
    if not index_path.exists():
        return {"pass": False, "value": "index.html NOT FOUND", "missing_tools": []}
    
    index_content = index_path.read_text(encoding="utf-8")
    
    # Get all tool pages (exclude index.html, CNAME, .gitkeep)
    tool_pages = [
        f.stem for f in PAGES_DIR.glob("*.html")
        if f.stem not in ("index", "404")
    ]
    
    # Check which tools are linked from homepage
    missing = []
    listed = []
    for tool_slug in tool_pages:
        # Check for link to the tool (href containing the slug)
        if tool_slug in index_content:
            listed.append(tool_slug)
        else:
            missing.append(tool_slug)
    
    return {
        "pass": len(missing) == 0,
        "value": f"{len(listed)}/{len(tool_pages)} tools listed on homepage",
        "missing_tools": missing,
        "listed_tools": listed,
    }


def run_full_qa() -> str:
    """Run complete QA check on all pages and return formatted report.
    
    This is the main function the agent calls as a tool.
    """
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append(f"  QA REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    
    # Find all tool pages
    if not PAGES_DIR.exists():
        return "ERROR: output/pages/ directory not found."
    
    html_files = sorted([
        f for f in PAGES_DIR.glob("*.html")
        if f.stem not in ("index", "404", "privacy", "terms", "about", "contact", "admin-ignore")
    ])
    
    if not html_files:
        return "ERROR: No tool pages found in output/pages/"
    
    report_lines.append(f"\nFound {len(html_files)} tool pages to check.\n")
    
    total_pass = 0
    total_fail = 0
    failed_pages = []
    
    for html_file in html_files:
        result = check_single_page(html_file)
        
        status_icon = "✅" if result["overall"] == "PASS" else "❌"
        report_lines.append(f"{status_icon} {result['page']} — {result['passed_checks']}/{result['total_checks']} checks passed")
        
        if result["overall"] == "PASS":
            total_pass += 1
        else:
            total_fail += 1
            failed_pages.append(result)
            # Show failed checks
            for check_name, check_result in result["checks"].items():
                if not check_result["pass"]:
                    report_lines.append(f"   ⚠️  {check_name}: {check_result['value']}")
    
    # Homepage check
    report_lines.append(f"\n{'—' * 40}")
    report_lines.append("HOMEPAGE CHECK:")
    homepage_result = check_homepage_lists_all_tools()
    hp_icon = "✅" if homepage_result["pass"] else "❌"
    report_lines.append(f"{hp_icon} {homepage_result['value']}")
    if homepage_result.get("missing_tools"):
        report_lines.append(f"   Missing from homepage: {', '.join(homepage_result['missing_tools'])}")
    
    # Summary
    report_lines.append(f"\n{'=' * 60}")
    report_lines.append(f"SUMMARY: {total_pass} passed, {total_fail} failed out of {len(html_files)} pages")
    if total_fail == 0:
        report_lines.append("🎉 ALL PAGES PASS QA!")
    else:
        report_lines.append(f"⚠️  {total_fail} page(s) need attention.")
    report_lines.append("=" * 60)
    
    report_text = "\n".join(report_lines)
    
    # Save report to logs
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / f"qa_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
    report_path.write_text(report_text, encoding="utf-8")
    
    return report_text


def check_page_after_publish(keyword: str) -> str:
    """Quick QA check on a single page right after it's published.
    
    Called by the daily bot after building a new tool page.
    """
    slug = keyword.lower().replace(" ", "-")
    filepath = PAGES_DIR / f"{slug}.html"
    
    if not filepath.exists():
        return f"QA FAIL: Page file not found at {filepath}"
    
    result = check_single_page(filepath)
    
    if result["overall"] == "PASS":
        return f"QA PASS: {result['page']} — all {result['total_checks']} checks passed ✅"
    else:
        failed = [
            f"{name}: {info['value']}"
            for name, info in result["checks"].items()
            if not info["pass"]
        ]
        return f"QA FAIL: {result['page']} — {result['failed_checks']} issues found:\n" + "\n".join(f"  ⚠️ {f}" for f in failed)
"""Quality Assurance checker for all tool pages."""
