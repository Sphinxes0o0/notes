"""Regression checks for links hidden by Markdown formatting and JSON output."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('link_check.py')


class LinkCheckTests(unittest.TestCase):
    def check_site(self, content, extra_files=()):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'index.md').write_text(content, encoding='utf-8')
            for name in extra_files:
                (root / name).write_text('# Target\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--root', folder, '--json'],
                capture_output=True, text=True, check=False,
            )
            return result.returncode, json.loads(result.stdout)

    def test_code_label_does_not_hide_missing_link(self):
        status, report = self.check_site('[`missing.md`](missing.md)\n')
        self.assertEqual(status, 1)
        self.assertEqual(report['internal']['broken_count'], 1)
        self.assertEqual(report['internal']['broken'][0]['link'], 'missing.md')

    def test_code_examples_are_not_links(self):
        status, report = self.check_site(
            '```python\n[example](missing.md)\n```\n'
            '`callbacks_[fd](revents)`\n'
        )
        self.assertEqual(status, 0)
        self.assertEqual(report['internal']['total'], 0)

    def test_published_html_links_resolve_to_markdown(self):
        status, report = self.check_site(
            '[`target`](target.html)\n[absolute](/target.html)\n',
            extra_files=['target.md'],
        )
        self.assertEqual(status, 0)
        self.assertEqual(report['internal']['total'], 2)
        self.assertEqual(report['internal']['broken_count'], 0)


if __name__ == '__main__':
    unittest.main()
