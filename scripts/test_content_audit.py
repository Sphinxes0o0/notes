import unittest
import tempfile
import subprocess
import sys
import json
import hashlib
from pathlib import Path
from content_audit import count_content_lines, prose_without_code


class ContentAuditTests(unittest.TestCase):
    def test_technical_lists_tables_and_code_contribute_content(self):
        text = '---\ntitle: Demo\n---\n# Title\n- item\n| cell |\n```python\nvalue = 1\n```\n'
        self.assertEqual(count_content_lines(text), 4)

    def test_nested_examples_do_not_create_prose_placeholders(self):
        text = '````markdown\n```python\nTODO\n```\n````\nactual prose\n'
        self.assertEqual(prose_without_code(text), 'actual prose')

    def test_frontmatter_is_not_body_content(self):
        self.assertEqual(prose_without_code('---\ndescription: TODO\n---\ntext'), 'text')

    def test_review_gate_reopens_after_file_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            page = root / 'note.md'
            page.write_text('---\ntitle: Note\n---\n# Note\nShort note.\n')
            script = Path(__file__).with_name('content_audit.py')
            def run():
                return subprocess.run([sys.executable, str(script), '--root', folder, '--strict', '--json'], capture_output=True).returncode
            self.assertEqual(run(), 1)
            (root / '.github').mkdir()
            ledger = {'reviews': {'note.md': {'sha256': hashlib.sha256(page.read_bytes()).hexdigest(), 'categories': ['stubs'], 'reason': 'Reviewed short reference.'}}}
            (root / '.github/content-review.json').write_text(json.dumps(ledger))
            self.assertEqual(run(), 0)
            page.write_text(page.read_text() + 'Changed.\n')
            self.assertEqual(run(), 1)


if __name__ == '__main__':
    unittest.main()
