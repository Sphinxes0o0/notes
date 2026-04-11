#!/usr/bin/env python3
import re
import os
import sys

def extract_language(pre_tag):
    """Extract language from <pre class="lang-xxx"> or <code data-language="xxx">"""
    match = re.search(r'class=["\']lang-(\w+)', pre_tag)
    if match:
        return match.group(1)
    match = re.search(r'data-language=["\'](\w+)', pre_tag)
    if match:
        return match.group(1)
    return 'text'

def strip_html_tags(text):
    """Remove HTML tags but keep text content"""
    # Replace <span class="...">...</span> with just content (but handle nested spans)
    # First handle self-closing tags
    text = re.sub(r'<br\s*/?>', '\n', text)

    # Handle span tags - extract content
    while '<span' in text:
        text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
        if '<span' not in text:
            break

    # Remove any remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Convert HTML entities
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&quot;', '"')

    return text

def convert_html_code_block(content):
    """Convert HTML code blocks to markdown format"""

    # Pattern to match <pre class="lang-xxx" data-nodeid="..."><code data-language="xxx">...</code></pre>
    # The content may span multiple lines

    # Find all <pre> tags with their content
    pattern = r'<pre\s+class="lang-(\w+)"[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>'

    def replace_pre_block(match):
        lang = match.group(1)
        inner_content = match.group(2)
        cleaned = strip_html_tags(inner_content)
        # Remove leading/trailing whitespace but preserve indentation
        lines = cleaned.split('\n')
        # Remove empty first/last lines if code is wrapped
        return f'```{lang}\n{cleaned}\n```'

    result = re.sub(pattern, replace_pre_block, content, flags=re.DOTALL)

    return result

def process_file(filepath):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has HTML code blocks
        if '<pre class="lang-' not in content:
            return False

        converted = convert_html_code_block(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(converted)

        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    directories = ['datastructure', 'design_patterns', 'network_fundamentals', 'os_fundamentals', 'misc']

    total_files = 0
    converted_files = 0

    for dir_name in directories:
        if not os.path.isdir(dir_name):
            continue

        for filename in os.listdir(dir_name):
            if filename.endswith('.md'):
                filepath = os.path.join(dir_name, filename)
                total_files += 1
                if process_file(filepath):
                    converted_files += 1
                    print(f"Converted: {filepath}")

    print(f"\nTotal files: {total_files}, Converted: {converted_files}")

if __name__ == '__main__':
    main()
