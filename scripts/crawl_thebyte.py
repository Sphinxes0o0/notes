#!/usr/bin/env python3
"""
Crawl pages from thebyte.com.cn and convert to markdown.
"""

import os
import re
import html
from pathlib import Path
from urllib.parse import urljoin, urlparse
import subprocess
import time

BASE_URL = "https://www.thebyte.com.cn"
OUTPUT_DIR = Path("/Users/sphinx.shi/workspace/wiki/pyramid/raw/bookmarks/ebooks/thebyte")
IMAGES_DIR = OUTPUT_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

CHAPTERS = {
    "consensus": [
        "/consensus/summary.html",
        "/consensus/consensus.html",
        "/consensus/Replicated-State-Machine.html",
        "/consensus/Paxos.html",
        "/consensus/Paxos-history.html",
        "/consensus/Basic-Paxos.html",
        "/consensus/Raft.html",
        "/consensus/raft-leader-election.html",
        "/consensus/raft-log-replication.html",
        "/consensus/raft-ConfChange.html",
    ],
    "container": [
        "/container/summary.html",
        "/container/borg-omega-k8s.html",
        "/container/orchestration.html",
        "/container/image.html",
        "/container/CRI.html",
        "/container/storage.html",
        "/container/container-network.html",
        "/container/Resource-scheduling.html",
        "/container/resource.html",
        "/container/Extended-Resource.html",
        "/container/kube-scheduler.html",
        "/container/auto-scaling.html",
    ],
}

def download_image(img_url, img_name, page_name):
    """Download an image and return the local path."""
    if not img_url or img_url.startswith('data:'):
        return None

    # Skip external URLs
    parsed = urlparse(img_url)
    if parsed.netloc and parsed.netloc != 'thebyte.com.cn' and parsed.netloc != 'www.thebyte.com.cn':
        return None

    local_name = f"{page_name}_{img_name}"
    local_path = IMAGES_DIR / local_name

    if local_path.exists():
        return local_name

    # Download with curl
    if img_url.startswith('/'):
        full_url = BASE_URL + img_url
    else:
        full_url = img_url

    try:
        subprocess.run(
            ["curl", "-s", "-L", "-o", str(local_path), full_url],
            check=True,
            timeout=30
        )
        if local_path.exists() and local_path.stat().st_size > 0:
            return local_name
        else:
            return None
    except Exception as e:
        print(f"  Failed to download {full_url}: {e}")
        return None


def extract_content(html_content, page_path):
    """Extract article content from HTML."""
    # Find theme-default-content div
    match = re.search(r'<div class="theme-default-content">(.*?)</div>\s*<!--\[-->\s*<!--\[-->\s*<div class="page-info"', html_content, re.DOTALL)
    if not match:
        # Try alternative pattern
        match = re.search(r'<div class="theme-default-content">(.*?)<div class="page-info"', html_content, re.DOTALL)

    if not match:
        print(f"  Could not find theme-default-content for {page_path}")
        return None

    return match.group(1)


def html_to_markdown(html_content, page_path, page_name):
    """Convert HTML content to markdown."""
    content = html_content

    # Track images for download
    images_to_download = []
    img_counter = 0

    # Extract and replace images
    def replace_img(match):
        nonlocal img_counter
        img_src = match.group(1)
        img_alt = match.group(2) if match.group(2) else f"image"

        if img_counter >= 8:
            return ""

        # Create a simple name for the image
        img_name = f"img{img_counter:02d}.png"
        img_counter += 1

        images_to_download.append((img_src, img_name))
        return f"\n![{img_alt}](../images/{page_name}_{img_name})\n"

    # Replace images
    content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>', replace_img, content)
    content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', replace_img, content)

    # Download images
    for img_src, img_name in images_to_download[:8]:
        download_image(img_src, img_name, page_name)

    # Remove VuePress comments
    content = re.sub(r'<!--\[-->|<!--\]-->|<!\[CDATA\[|\]\]>', '', content)

    # Remove empty comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)

    # Remove style tags
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

    # Remove header anchors
    content = re.sub(r'<a class="header-anchor"[^>]*>[^<]*</a>', '', content)

    # Remove giscus wrapper
    content = re.sub(r'<div class="giscus-wrapper[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Remove qrcode div
    content = re.sub(r'<div class="qrcode"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Remove page-nav
    content = re.sub(r'<div class="page-nav[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Remove page-meta footer
    content = re.sub(r'<footer class="page-meta[^"]*"[^>]*>.*?</footer>', '', content, flags=re.DOTALL)

    # Remove data-v attributes
    content = re.sub(r'\s*data-v-[a-z0-9]+="[^"]*"', '', content)
    content = re.sub(r'\s*data-v-[a-z0-9]+', '', content)

    # Extract title
    title_match = re.search(r'<h1[^>]*id="([^"]*)"[^>]*>([^<]*)</h1>', content)
    title = title_match.group(2) if title_match else os.path.basename(page_path).replace('.html', '')

    # Remove h1 since we'll add it in frontmatter
    content = re.sub(r'<h1[^>]*>.*?</h1>', '', content, flags=re.DOTALL)

    # Process custom containers (tip, warning, danger, info)
    def replace_container(match):
        container_type = match.group(1)
        inner = match.group(2)
        # Extract title if exists
        title_match = re.search(r'<p class="custom-container-title"><a></a></p>\s*<p>([^<]*)</p>', inner)
        title = title_match.group(1) if title_match else ""
        # Get paragraph content
        p_match = re.search(r'<p>([^<].*?)</p>', inner, re.DOTALL)
        text = p_match.group(1) if p_match else inner
        text = re.sub(r'<[^>]+>', '', text).strip()
        if title:
            return f"\n> **{title}** {text}\n"
        return f"\n> {text}\n"

    content = re.sub(r'<div class="custom-container ([^"]+)">\s*<p class="custom-container-title"><a></a></p>(.*?)</div>', replace_container, content, flags=re.DOTALL)

    # Process div custom-container (center, right)
    content = re.sub(r'<div class="custom-container center">\s*<p>(.*?)</p>\s*</div>', r'\n<div align="center">\1</div>\n', content, flags=re.DOTALL)
    content = re.sub(r'<div class="custom-container right">\s*<p>(.*?)</p>\s*</div>', r'\n<div align="right">\1</div>\n', content, flags=re.DOTALL)

    # Remove remaining divs
    content = re.sub(r'</?div[^>]*>', '', content)

    # Convert headers
    content = re.sub(r'<h(\d)[^>]*>([^<]*)</h\1>', r'\n## \2\n', content)

    # Convert paragraphs
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', content, flags=re.DOTALL)

    # Convert line breaks
    content = re.sub(r'<br\s*/?>','\n', content)

    # Convert strong/bold
    content = re.sub(r'<strong[^>]*>([^<]*)</strong>', r'**\1**', content)
    content = re.sub(r'<b[^>]*>([^<]*)</b>', r'**\1**', content)

    # Convert emphasis
    content = re.sub(r'<em[^>]*>([^<]*)</em>', r'*\1*', content)

    # Convert links
    content = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', r'[\2](\1)', content)

    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Decode HTML entities
    content = html.unescape(content)

    # Clean up whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()

    return title, content


def process_page(url_path):
    """Process a single page."""
    url = BASE_URL + url_path
    print(f"Processing: {url_path}")

    # Determine output path
    if url_path.startswith('/'):
        rel_path = url_path.lstrip('/')
    else:
        rel_path = url_path

    # Convert .html to .md
    if rel_path.endswith('.html'):
        md_path = rel_path.replace('.html', '.md')
    else:
        md_path = rel_path + '.md'

    output_file = OUTPUT_DIR / md_path

    # Create parent directories
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Fetch HTML
    result = subprocess.run(
        ["curl", "-s", "-L", url],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(f"  Failed to fetch {url}")
        return False

    html_content = result.stdout

    # Extract title
    title_match = re.search(r'<title>([^<]*)</title>', html_content)
    page_title = title_match.group(1) if title_match else os.path.basename(url_path)

    # Extract content
    content = extract_content(html_content, url_path)
    if not content:
        print(f"  Could not extract content from {url_path}")
        return False

    # Convert to markdown
    article_title, md_content = html_to_markdown(content, url_path, md_path.replace('/', '_').replace('.md', ''))

    # Build full markdown
    frontmatter = f"""---
title: "{article_title}"
source: thebyte
url: "{url}"
---

"""
    full_md = frontmatter + md_content

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_md)

    print(f"  Saved: {output_file}")
    return True


def main():
    total = 0
    success = 0

    for chapter, pages in CHAPTERS.items():
        print(f"\n=== Processing {chapter} ===")
        for page in pages:
            total += 1
            if process_page(page):
                success += 1
            time.sleep(0.5)  # Be polite

    print(f"\n\nDone: {success}/{total} pages processed successfully")


if __name__ == "__main__":
    main()