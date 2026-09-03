"""Script to inject Viral Action Bar and Embed Modal into all tool pages."""
from pathlib import Path

pages_dir = Path("output/pages")
tool_files = [
    f for f in pages_dir.glob("*.html")
    if f.stem not in ("index", "404", "privacy", "terms", "about", "contact", "admin-ignore")
]

css_snippet = """        /* Tool Action Bar */
        .tool-action-bar {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 16px 0 24px 0;
            flex-wrap: wrap;
        }
        .btn-action-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #cbd5e1;
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            user-select: none;
        }
        .btn-action-pill:hover {
            background: rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.4);
            color: #93c5fd;
            transform: translateY(-1px);
        }
        .btn-action-pill.copied {
            background: rgba(34, 197, 94, 0.2);
            border-color: rgba(34, 197, 94, 0.4);
            color: #4ade80;
        }

        /* Embed Modal */
        .embed-modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .embed-modal-box {
            background: #121216;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            max-width: 540px;
            width: 100%;
            padding: 24px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
        }
        .embed-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .embed-modal-header h3 {
            font-family: 'Syne', sans-serif;
            font-size: 1.15rem;
            color: #fff;
            margin: 0;
        }
        .embed-close-btn {
            background: transparent;
            border: none;
            color: #94a3b8;
            font-size: 1.4rem;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }
        .embed-code-textarea {
            width: 100%;
            height: 110px;
            background: #09090b;
            color: #38bdf8;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            resize: none;
            box-sizing: border-box;
            margin-bottom: 14px;
        }
"""

toolbar_snippet = """
        <!-- Viral Share & Embed Toolbar -->
        <div class="tool-action-bar">
            <button class="btn-action-pill" onclick="copyToolShareUrl(this)">
                <span>🔗</span> Copy Link
            </button>
            <a href="https://twitter.com/intent/tweet" class="btn-action-pill share-twitter-btn" target="_blank" rel="noopener">
                <span>𝕏</span> Share
            </a>
            <a href="https://www.linkedin.com/sharing/share-offsite/" class="btn-action-pill share-linkedin-btn" target="_blank" rel="noopener">
                <span>in</span> LinkedIn
            </a>
            <button class="btn-action-pill" onclick="openEmbedModal()">
                <span>&lt;/&gt;</span> Embed Tool
            </button>
        </div>
"""

modal_js_snippet = """
    <script>
        // Dynamic share links and embed snippet
        document.addEventListener('DOMContentLoaded', () => {
            const curUrl = window.location.href;
            const toolHeading = document.querySelector('h1') ? document.querySelector('h1').innerText : 'Developer Utility';
            
            const twBtn = document.querySelector('.share-twitter-btn');
            if (twBtn) {
                twBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent('Check out this fast, free developer tool: ' + toolHeading)}&url=${encodeURIComponent(curUrl)}`;
            }
            const liBtn = document.querySelector('.share-linkedin-btn');
            if (liBtn) {
                liBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(curUrl)}`;
            }

            const embedSnippet = `<iframe src="${curUrl}" width="100%" height="650" frameborder="0" style="border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; max-width: 900px; width: 100%;"></iframe>\\n<p style="font-size: 12px; color: #64748b;">Tool powered by <a href="${curUrl}" target="_blank" rel="noopener">AI Tool Suite</a></p>`;
            const embedArea = document.getElementById('embedSnippetText');
            if (embedArea) embedArea.value = embedSnippet;
        });

        function copyToolShareUrl(btn) {
            navigator.clipboard.writeText(window.location.href).then(() => {
                const orig = btn.innerHTML;
                btn.innerHTML = '<span>✅</span> Link Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.innerHTML = orig;
                    btn.classList.remove('copied');
                }, 2000);
            });
        }

        function openEmbedModal() {
            const m = document.getElementById('embedModal');
            if (m) m.style.display = 'flex';
        }

        function closeEmbedModal() {
            const m = document.getElementById('embedModal');
            if (m) m.style.display = 'none';
        }

        function copyEmbedSnippet(btn) {
            const snippet = document.getElementById('embedSnippetText').value;
            navigator.clipboard.writeText(snippet).then(() => {
                const orig = btn.innerText;
                btn.innerText = 'Copied to Clipboard!';
                setTimeout(() => btn.innerText = orig, 2000);
            });
        }
    </script>

    <!-- Embed Modal Dialog -->
    <div id="embedModal" class="embed-modal-overlay" onclick="if(event.target === this) closeEmbedModal()">
        <div class="embed-modal-box">
            <div class="embed-modal-header">
                <h3>Embed this Tool on Your Site</h3>
                <button class="embed-close-btn" onclick="closeEmbedModal()">&times;</button>
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 12px; line-height: 1.5;">
                Copy and paste this snippet into your blog, documentation, or tech site to embed this interactive utility:
            </p>
            <textarea id="embedSnippetText" class="embed-code-textarea" readonly></textarea>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="btn-action-pill" onclick="closeEmbedModal()">Close</button>
                <button class="btn-action-pill" style="background: #3b82f6; color: #fff; border-color: #3b82f6;" onclick="copyEmbedSnippet(this)">
                    Copy Embed Code
                </button>
            </div>
        </div>
    </div>
"""

updated = 0
for f in tool_files:
    content = f.read_text(encoding="utf-8")
    if "tool-action-bar" in content:
        continue
    
    # 1. Inject CSS before /* Tool Interactive Surface */
    if "/* Tool Interactive Surface */" in content:
        content = content.replace("/* Tool Interactive Surface */", css_snippet + "\n        /* Tool Interactive Surface */")
    elif "</style>" in content:
        content = content.replace("</style>", css_snippet + "\n    </style>")
        
    # 2. Inject Toolbar right after </header>
    if "</header>" in content:
        content = content.replace("</header>", "</header>" + toolbar_snippet)
        
    # 3. Inject Modal & JS before </body>
    if "</body>" in content:
        content = content.replace("</body>", modal_js_snippet + "\n</body>")
        
    f.write_text(content, encoding="utf-8")
    updated += 1

print(f"Updated {updated} / {len(tool_files)} tool pages with Viral Action Bar & Embed Modal!")
