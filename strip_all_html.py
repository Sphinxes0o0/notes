#!/usr/bin/env python3
import re
import os

def strip_html(content):
    """Strip HTML tags but preserve text content"""
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

def main():
    directories = ['datastructure', 'design_patterns', 'network_fundamentals', 'os_fundamentals']

    converted = 0
    for dir_name in directories:
        if not os.path.isdir(dir_name):
            continue

        for filename in os.listdir(dir_name):
            if filename.endswith('.md'):
                filepath = os.path.join(dir_name, filename)
                if process_file(filepath):
                    print(f"Fixed: {filepath}")
                    converted += 1

    print(f"\nTotal files fixed: {converted}")

if __name__ == '__main__':
    main()
