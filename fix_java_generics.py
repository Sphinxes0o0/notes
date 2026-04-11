#!/usr/bin/env python3
import re
import os

def strip_all_html(content):
    """Strip ALL HTML/XML-like tags completely"""
    # Replace <word> patterns that look like Java generics with just the word
    # This handles <Integer>, <String>, <Object>, etc.
    content = re.sub(r'<([A-Za-z_][A-Za-z0-9_]*)>', r'\1', content)

    # Replace <...> with empty for any remaining angle brackets
    content = re.sub(r'<[^>]*>', '', content)

    # Convert HTML entities
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&amp;', '&')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&quot;', '"')

    return content

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        converted = strip_all_html(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(converted)
        return True
    except Exception as e:
        print(f"Error: {filepath}: {e}")
        return False

# Fix all datastructure files
for f in os.listdir('datastructure'):
    if f.endswith('.md'):
        process_file(f'datastructure/{f}')
        print(f"Fixed: datastructure/{f}")
