#!/usr/bin/env python3
"""Check built pages, local resources and published link targets against a running preview.

Start npm run docs:preview, then run this script (default port 4173).
Use --base-url http://127.0.0.1:PORT/notes/ for another preview port.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.request import ProxyHandler, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:4173/notes/')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent / '.vitepress/dist'
    base = args.base_url.rstrip('/') + '/'
    origin = urlsplit(base).netloc
    opener = build_opener(ProxyHandler({}))
    destinations = {}
    ids_by_path = {}
    fragments = []
    pages = list(root.rglob('*.html'))
    if not pages:
        raise SystemExit('No built pages; run npm run docs:build first')

    class References(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if attrs.get('id'):
                self.ids.add(attrs['id'])
            if tag == 'a' and attrs.get('name'):
                self.ids.add(attrs['name'])
            if tag == 'a' and attrs.get('href'):
                target = urlsplit(urljoin(current, attrs['href']))
                if target.netloc == origin and target.fragment:
                    fragments.append((source, unquote(target.path), unquote(target.fragment), attrs['href']))
            values = []
            if tag in ('img', 'script', 'source'):
                values.append(attrs.get('src', ''))
            if tag == 'a' or (tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon', 'modulepreload', 'preload')):
                values.append(attrs.get('href', ''))
            for value in values:
                if not value or value.startswith('#'):
                    continue
                url = urlsplit(urljoin(current, value))
                if url.netloc == origin:
                    destinations.setdefault(url._replace(fragment='').geturl(), source)

    for page in pages:
        source = page.relative_to(root).as_posix()
        route = source[:-10] if source.endswith('index.html') else source[:-5]
        current = urljoin(base, route)
        destinations.setdefault(current, source)
        references = References()
        references.feed(page.read_text(encoding='utf-8'))
        for alias in [current, urljoin(base, source), current.rstrip('/')]:
            ids_by_path[unquote(urlsplit(alias).path)] = references.ids
    for index in (root / 'assets').glob('search-index-*.json*'):
        destinations[urljoin(base, 'assets/' + index.name)] = 'search index'

    legacy = {}
    source_root = Path(__file__).resolve().parent.parent
    for mapping, owner in {
        'ccpp/cpp/abseil-hints/legacy-anchors.json': 'ccpp/cpp/abseil-hints',
        'coding_agent/pi-agent/legacy-anchors.json': 'coding_agent/pi-agent',
        'security/nids/snort3/legacy-anchors.json': 'security/nids/snort3_architecture_analysis',
    }.items():
        targets = json.loads((source_root / mapping).read_text(encoding='utf-8'))
        legacy[urlsplit(urljoin(base, owner)).path] = set(targets)
        for old, target in targets.items():
            url = urlsplit(urljoin(base, target.lstrip('/')))
            destinations.setdefault(url._replace(fragment='').geturl(), mapping)
            fragments.append((mapping, unquote(url.path), unquote(url.fragment), target))
    fragment_failures = []
    for source, target, anchor, href in fragments:
        if target in ids_by_path and anchor not in ids_by_path[target] and anchor not in legacy.get(target, set()):
            fragment_failures.append({'source': source, 'href': href, 'missing_anchor': anchor})

    deadline = time.monotonic() + 20
    while True:
        try:
            with opener.open(base, timeout=2):
                break
        except OSError:
            if time.monotonic() >= deadline:
                raise SystemExit('Preview server did not become ready')
            time.sleep(0.1)

    def check(url):
        try:
            with opener.open(quote(url, safe=':/+%?=&'), timeout=30) as response:
                if response.status == 200 and response.read():
                    return None
                return {'url': url, 'source': destinations[url], 'status': response.status}
        except OSError as error:
            return {'url': url, 'source': destinations[url], 'error': str(error)}

    with ThreadPoolExecutor(max_workers=12) as pool:
        failures = [result for result in pool.map(check, destinations) if result]
    print(json.dumps({'pages': len(pages), 'destinations': len(destinations), 'fragment_checks': len(fragments), 'failures': failures, 'fragment_failures': fragment_failures}, ensure_ascii=False, indent=2))
    return int(bool(failures or fragment_failures))


if __name__ == '__main__':
    raise SystemExit(main())
