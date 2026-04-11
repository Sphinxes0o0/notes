#!/usr/bin/env python3
import re
import os

def strip_html(content):
    """Strip HTML tags but preserve paragraph text with newlines"""
    # Replace <br> with newlines
    content = re.sub(r'<br\s*/?>', '\n', content)

    # Remove all HTML tags but keep content
    content = re.sub(r'<[^>]+>', '', content)

    # Clean up multiple newlines
    content = re.sub(r'\n\n+', '\n\n', content)

    # Convert HTML entities
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&amp;', '&')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&quot;', '"')

    return content

def process_file(filepath):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has HTML-like tags with data-nodeid
        if 'data-nodeid=' not in content:
            return False

        # Strip HTML tags
        converted = strip_html(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(converted)

        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

# Fix the specific file
filepath = 'datastructure/15_定位问题才能更好地解决问题_开发前的复杂度分析与技术选型.md'
if process_file(filepath):
    print(f"Fixed: {filepath}")
else:
    print(f"No changes: {filepath}")
