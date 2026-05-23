#!/usr/bin/env python3
"""Check files with corrupt line-number prefixes."""
import os

WIKI = "/Users/sphinx/github/pyramid/wiki"
corrupt = []
for root, dirs, files in os.walk(WIKI):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'attachments']
    for f in files:
        if not f.endswith('.md'):
            continue
        full = os.path.join(root, f)
        with open(full, 'rb') as fh:
            first_bytes = fh.read(20)
        # Check if file starts with spaces and contains line number pattern
        if first_bytes and first_bytes[0:5] == b'     ' and b'|' in first_bytes[:15]:
            rel = os.path.relpath(full, WIKI)
            corrupt.append(rel)
            print(f"CORRUPT: {rel}")

if not corrupt:
    print("No corrupt files found")
else:
    print(f"\nTotal corrupt files: {len(corrupt)}")
