#!/usr/bin/env python3
"""Verify the Pyramid import against its preserved source Git tree (read-only)."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / '.github/pyramid-import.json').read_text())


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false', *args])


def entries(tree):
    result = {}
    for row in git('ls-tree', '-rz', tree).split(b'\0'):
        if row:
            head, name = row.split(b'\t', 1)
            mode, kind, sha = head.decode().split()
            result[name.decode()] = (mode, kind, sha)
    return result


def main():
    source = entries(META['source_commit'])
    lfs = {item['path']: item for item in META['lfs']}
    errors = []
    checked = 0
    for name, (mode, kind, sha) in source.items():
        if any(name.startswith(prefix) for prefix in META['excluded']) or name in META['changed_files']:
            continue
        target = META['prefix'] + name
        rows = git('ls-files', '--stage', '-z', '--', target).split(b'\0')
        rows = [row for row in rows if row]
        if len(rows) != 1:
            errors.append(f'{target}: missing or unexpected index entry')
            continue
        actual_mode, actual_sha, stage = rows[0].split(b'\t')[0].decode().split()
        if mode != actual_mode or stage != '0':
            errors.append(f'{target}: mode or merge stage changed')
        if name in lfs:
            content = git('cat-file', 'blob', actual_sha)
            item = lfs[name]
            if len(content) != item['size'] or hashlib.sha256(content).hexdigest() != item['oid']:
                errors.append(f'{target}: hydrated LFS content differs')
        elif actual_sha != sha:
            errors.append(f'{target}: source Git object differs')
        checked += 1
    if git('ls-files', '--', META['prefix'] + 'scripts/node_modules'):
        errors.append('Imported node_modules must not be tracked')
    for ancestor in [META['source_commit'], META['source_remote_main'], META['notes_base']]:
        if subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', ancestor, 'HEAD']).returncode:
            errors.append(f'History is not preserved: {ancestor}')
    print(f'Pyramid import: {checked} source entries, {len(lfs)} hydrated LFS files, {len(errors)} errors.')
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
