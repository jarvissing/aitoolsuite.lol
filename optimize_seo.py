import os
import re

root_dir = r"C:/Users/admin/aitoolsuite.lol"

exclude_files = {'index.html', 'privacy.html', 'terms.html', 'about.html', 'contact.html', 'admin-ignore.html'}

html_files = [f for f in os.listdir(root_dir) if f.endswith('.html') and f not in exclude_files]

print(f"Found {len(html_files)} tool pages to audit and optimize for SEO.")

schema_template = '''
    <!-- Automated SEO & Schema Markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "%s",
      "operatingSystem": "All",
      "applicationCategory": "DeveloperApplication",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "description": "%s"
    }
    </script>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Is my data secure and private?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes! All processing happens 100%% locally inside your browser via client-side JavaScript. No data is ever transmitted or stored on remote servers."
          }
        },
        {
          "@type": "Question",
          "name": "Is this tool free to use?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, 100%% free with zero ads, zero paywalls, and no login required."
          }
        }
      ]
    }
    </script>
'''

updated_count = 0

for filename in html_files:
    filepath = os.path.join(root_dir, filename)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Skip if already has SoftwareApplication schema
    if 'SoftwareApplication' in content:
        continue

    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else filename.replace('.html', '').replace('-', ' ').title()

    # Extract description
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content, re.IGNORECASE)
    desc = desc_match.group(1).strip() if desc_match else f"Free online {title.lower()} utility running 100%% client-side with instant results."

    # Escape quotes
    clean_title = title.replace('"', '\\"')
    clean_desc = desc.replace('"', '\\"')

    injected_schemas = schema_template % (clean_title, clean_desc)

    # Insert before </head>
    if '</head>' in content:
        new_content = content.replace('</head>', injected_schemas + '\n</head>')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated_count += 1

print(f"Successfully injected SEO schema and FAQ structured data into {updated_count} tool pages!")
