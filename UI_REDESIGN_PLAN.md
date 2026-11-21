# UI Redesign Plan — aitoolsuite.lol

> **Purpose**: This is a complete, self-contained redesign brief. Paste this into your coding session and say "Execute this plan." Everything needed to implement is here.

---

## What This Site Is

aitoolsuite.lol is a static site with 100+ free browser-based developer/AI utilities. Built with Jinja2 templates (Python), deployed to Netlify. Two template files control the entire site's look:

- `templates/homepage_template.html` — the index page (hero, search, tool grid)
- `templates/tool_page_template.html` — every individual tool page

After editing templates, run `python tools/homepage_updater.py` to regenerate `index.html`.

---

## Current Problems (Why It Looks AI-Generated)

1. **Inter + Syne fonts** — the #1 most common AI-generated font combo
2. **`#3b82f6` Tailwind blue accent** — every AI tool site uses this exact blue
3. **ALL-CAPS labels** everywhere (`text-transform: uppercase; letter-spacing: 0.05em`)
4. **Identical rounded cards** — same 16px radius, same shadow, same hover translateY(-3px)
5. **`↗` arrow on every card** — template chrome
6. **Pill-shaped hero badge** with emoji (`⚡ 106 Free Production Tools`)
7. **Single accented word in headline** (`built for <span>speed.</span>` with blue span)
8. **100px border-radius pill navbar** — the default AI floating nav
9. **Purple/indigo affiliate badges** — generic SaaS palette
10. **Emoji in section headers** (⚡🛠️📝🎨🔍)

---

## Design Direction: "Dark Workshop"

The site is a developer workshop — tools you grab and use. Not a SaaS product pitch. The aesthetic should feel purposeful, high-contrast, slightly industrial. One warm accent, sharp edges, no decoration that doesn't earn its space.

---

## Design Tokens

### Colors

```
--void:           #0a0a0c    /* page background */
--surface:        #141418    /* card/elevated surfaces */
--surface-hover:  #1a1a20    /* card hover state */
--rule:           #232328    /* borders, dividers */
--text-primary:   #e8e8ec    /* headings, primary text */
--text-secondary: #7a7a86    /* descriptions, meta */
--text-tertiary:  #4a4a54    /* footer, fine print */
--signal:         #e2a53a    /* THE accent — warm amber/gold */
--signal-dim:     rgba(226, 165, 58, 0.12)  /* amber background tints */
--signal-border:  rgba(226, 165, 58, 0.3)   /* amber border highlights */
```

### Typography

Replace the Google Fonts import with:

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
```

| Role | Font | Weight | Usage |
|---|---|---|---|
| Headings | Space Grotesk | 700 | h1, h2, nav brand, card titles |
| Body | IBM Plex Sans | 400, 500, 600 | paragraphs, descriptions, nav links, buttons |
| Mono | IBM Plex Mono | 500 | search shortcut badge, tool counts, code labels |

### Spacing / Radius

- Card border-radius: `8px` (not 16px — sharper)
- Nav border-radius: `8px` (not 100px pill)
- Search bar border-radius: `6px` (not 100px pill)
- Button/badge radius: `4px`
- No `translateY(-3px)` hover lifts anywhere

---

## Specific Changes to Implement

### 1. Navbar

**Before**: Pill-shaped (border-radius: 100px), glowing blue dot, emoji-style
**After**: Slim angular bar (border-radius: 8px), no dot, tighter padding

```css
.site-nav {
    max-width: 980px;
    margin: 0 auto;
    background: rgba(20, 20, 24, 0.9);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--rule);
    border-radius: 8px;
    padding: 8px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```

Remove `.nav-brand-dot` entirely. Brand is just text:
```html
<a href="/" class="nav-brand">aitoolsuite</a>
```

Nav links: sentence case, no uppercase. Hover shows amber underline, not background fill.

### 2. Hero Section

**Before**:
```html
<div class="hero-badge">⚡ 106 Free Production Tools</div>
<h1>The Developer & AI Suite built for <span>speed.</span></h1>
<p>High-performance web utilities that run 100% inside your browser. No sign-ups, no paywalls, and zero tracking.</p>
```

**After**:
```html
<h1>{{ total_tools }} tools that run in your browser.</h1>
<p>No accounts. No tracking. Just utilities.</p>
```

- Kill the badge entirely
- Kill the `<span>` accent — one color headline
- Tighten the copy — say less, mean more
- h1 font-size stays large, color is `var(--text-primary)`, no blue

### 3. Search Bar

**Before**: Pill-shaped, blue focus glow, emoji 🔍
**After**: Sharp rectangle (6px radius), amber focus ring, SVG search icon or plain text

```css
.search-box {
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: 6px;
    padding: 8px 16px;
    transition: border-color 0.2s ease;
}
.search-box:focus-within {
    border-color: var(--signal);
    box-shadow: 0 0 0 1px var(--signal-border);
}
```

Replace the emoji search icon `🔍` with a plain SVG or the word "Search" as placeholder text.

### 4. Category Section Headers

**Before**:
```html
<h2 class="category-title">⚡ AI Utilities</h2>
<span class="category-count">8 TOOLS</span>  <!-- uppercase -->
```

**After**:
```html
<h2 class="category-title">{{ category.name }}</h2>
<span class="category-count">{{ category.tools|length }}</span>
```

- Remove emoji from display (keep `category.icon` in data, just don't render it)
- Category count: just the number, or "8 tools" in sentence case with monospace font
- Thin `1px solid var(--rule)` bottom border — no padding-bottom bloat

### 5. Tool Cards

**Before**: 16px radius, uppercase pill label, `↗` arrow, blue hover border, translateY lift
**After**: 8px radius, no pill label, no arrow, amber left-border glow on hover

```css
.tool-card {
    background: var(--surface);
    border: 1px solid var(--rule);
    border-left: 2px solid transparent;
    border-radius: 8px;
    padding: 20px;
    text-decoration: none;
    color: inherit;
    transition: border-color 0.2s ease, background 0.2s ease;
}
.tool-card:hover {
    border-left-color: var(--signal);
    background: var(--surface-hover);
}
```

Card HTML simplified — remove `.card-top`, `.pill-category`, `.card-arrow`:
```html
<a href="/{{ tool.slug }}.html" class="tool-card">
    <h3>{{ tool.name }}</h3>
    <p>{{ tool.description }}</p>
</a>
```

### 6. Affiliate Section

- Replace purple badge (`#818cf8`) with amber: `background: var(--signal-dim); border-color: var(--signal-border); color: var(--signal);`
- Badge text: "Sponsored" in sentence case, not "FREE TIER" uppercase
- Remove gradient backgrounds on affiliate cards — use flat `var(--surface)`
- CTA links: amber colored, no `↗`

### 7. Footer

- Remove emoji
- Sentence case
- Footer links: `color: var(--text-secondary)` with amber hover
- Copy: "Free. Private. Open." — three words, period.

### 8. Hero Animation (One Orchestrated Moment)

Add a single fade-in on page load for the hero content only. No per-card animations.

```css
@keyframes hero-enter {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
header h1, header p, .search-box-wrapper {
    animation: hero-enter 0.6s ease-out both;
}
header p { animation-delay: 0.1s; }
.search-box-wrapper { animation-delay: 0.2s; }

@media (prefers-reduced-motion: reduce) {
    header h1, header p, .search-box-wrapper {
        animation: none;
    }
}
```

No other animations. No card entrance effects. No section reveals.

### 9. Mobile (640px breakpoint)

- Nav: stack to full-width, keep 8px radius
- Search: full width, same sharp style
- Cards: single column, same amber hover
- Hide nav links behind a simple toggle or keep them scrollable

---

## What NOT to Change

- All Jinja2 template variables (`{{ }}` and `{% %}`)
- GoatCounter analytics script
- Search filter JavaScript logic
- Affiliate link URLs and disclosure text
- `robots.txt`, `sitemap.xml`, `favicon.svg`
- Widget files in `widgets/`
- Python build tools in `tools/`
- All tool page functional content (only restyle the chrome/wrapper)

---

## File Checklist

1. [ ] Edit `templates/homepage_template.html` — apply all changes above
2. [ ] Edit `templates/tool_page_template.html` — match the same design tokens, fonts, nav, footer, card styles
3. [ ] Run `python tools/homepage_updater.py` to regenerate index.html
4. [ ] Verify the generated `index.html` looks correct
5. [ ] Spot-check 2-3 individual tool pages for consistent styling

---

## Quick Validation After Build

Open the site and check:
- [ ] No Inter or Syne fonts loading (check Network tab)
- [ ] No blue `#3b82f6` anywhere (search CSS for it — should be zero hits)
- [ ] No ALL-CAPS text-transform on labels
- [ ] No `↗` arrows on cards
- [ ] No emoji in section headers
- [ ] Amber accent visible on: search focus, card hover, affiliate badges
- [ ] Hero fades in on load
- [ ] Mobile layout works at 375px width
