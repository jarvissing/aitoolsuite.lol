"""Tool page generation and publishing module."""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from config.settings import PAGES_DIR, SITE_NAME, TEMPLATES_DIR, QUEUE_PATH, SITE_URL

def build_tool_page(keyword: str, tool_name: str, description: str, category: str, faq_items: str, related_tools: str = "", tool_type: str = "") -> str:
    """
    Builds a tool page using a Jinja2 template and saves it to output/pages/.
    """
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    slug = keyword.lower().replace(" ", "-")
    output_path = PAGES_DIR / f"{slug}.html"
    
    faq_list = []
    if faq_items:
        pairs = faq_items.split("|||")
        for pair in pairs:
            if ":::" in pair:
                q, a = pair.split(":::", 1)
                faq_list.append({"question": q.strip(), "answer": a.strip()})
                
    related_list = [rt.strip() for rt in related_tools.split(",")] if related_tools else []
    
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template("tool_page_template.html")
    except Exception as e:
        # Fallback if template doesn't exist yet
        return f"Error loading template: {str(e)}. Ensure templates/tool_page_template.html exists."
        
    meta_title = f"{tool_name} - Free Online {category} Tool | {SITE_NAME}"
    page_slug = slug
    page_url = f"{SITE_URL}/{slug}"
    category_slug = category.lower().replace(" ", "-").replace("&", "and")

    related_tool_list = []
    for rt in related_list:
        rt_slug = rt.lower().replace(" ", "-")
        related_tool_list.append({"name": rt, "slug": rt_slug})

    # Load the correct widget HTML based on tool_type
    widget_html = ""
    widgets_dir = PAGES_DIR.parent.parent / "widgets"
    widget_map_path = widgets_dir / "widget_map.json"

    if tool_type:
        # Try to find widget by tool_type
        slug_type = tool_type.lower().replace(" ", "-")
        
        # Check widget_map.json first
        if widget_map_path.exists():
            try:
                widget_map = json.loads(widget_map_path.read_text())
                widget_file = widget_map.get(slug_type, "")
                if widget_file:
                    widget_path = widgets_dir / widget_file
                    if widget_path.exists():
                        widget_html = widget_path.read_text(encoding="utf-8")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Fallback: try direct filename match
        if not widget_html:
            direct_path = widgets_dir / f"{slug_type}.html"
            if direct_path.exists():
                widget_html = direct_path.read_text(encoding="utf-8")

    # If no widget found, use a placeholder
    if not widget_html:
        widget_html = '<div class="tool-widget-placeholder"><p>🔧 Interactive tool coming soon.</p></div>'

    from datetime import datetime
    html_content = template.render(
        tool_name=tool_name,
        description=description,
        category=category,
        category_name=category,
        category_slug=category_slug,
        faq_items=faq_list,
        related_tools=related_tool_list,
        meta_title=meta_title,
        meta_description=description,
        page_url=page_url,
        site_url=SITE_URL,
        site_name=SITE_NAME,
        slug=slug,
        year=datetime.now().year,
        widget_html=widget_html,
        tool_widget_html=widget_html,
    )

    output_path.write_text(html_content, encoding="utf-8")
    return f"SUCCESS: Page created at {output_path} | URL: {page_url}"

def check_existing_tool(keyword: str) -> str:
    """
    Checks if a page already exists for this keyword.
    """
    slug = keyword.lower().replace(" ", "-")
    output_path = PAGES_DIR / f"{slug}.html"
    
    if output_path.exists():
        return f"EXISTS: {output_path}"
        
    if QUEUE_PATH.exists():
        try:
            queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
            for item in queue:
                if item.get("keyword") == keyword and item.get("status") == "published":
                    return f"EXISTS_IN_QUEUE: {keyword} is marked published."
        except json.JSONDecodeError:
            pass
            
    return "NOT_FOUND"

def mark_tool_published(keyword: str, url: str) -> str:
    """
    Updates tool_queue.json setting status to published.
    """
    import datetime
    
    if not QUEUE_PATH.exists():
        QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_PATH.write_text("[]", encoding="utf-8")
        
    try:
        queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        queue = []
        
    updated = False
    for item in queue:
        if item.get("keyword") == keyword:
            item["status"] = "published"
            item["published_date"] = datetime.datetime.now().isoformat()
            item["url"] = url
            updated = True
            break
            
    if not updated:
        queue.append({
            "keyword": keyword,
            "status": "published",
            "published_date": datetime.datetime.now().isoformat(),
            "url": url
        })
        
    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return f"Successfully marked '{keyword}' as published."

def get_next_pending_tool() -> str:
    """
    Returns the first item with status 'pending' from the tool queue.
    """
    if not QUEUE_PATH.exists():
        return "QUEUE_EMPTY"
        
    try:
        queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        for item in queue:
            if item.get("status") == "pending":
                return json.dumps(item, indent=2)
    except json.JSONDecodeError:
        pass
        
    return "QUEUE_EMPTY"
