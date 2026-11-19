#!/usr/bin/env python3
"""Fix corrupt files that have line-number prefixes."""
import re

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    # Remove line-number prefix "     N|" from each line
    fixed = re.sub(r'^\s+\d+\|', '', content, flags=re.MULTILINE)
    
    with open(path, 'w') as f:
        f.write(fixed)
    
    lines_before = content.count('\n') + 1
    lines_after = fixed.count('\n') + 1
    print(f"Fixed: {path} ({lines_before} lines -> {lines_after} lines)")

fix_file("/Users/sphinx/github/pyramid/wiki/home.md")
fix_file("/Users/sphinx/github/pyramid/wiki/log.md")
print("Done fixing corrupt files.")
