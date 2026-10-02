#!/usr/bin/env python3
"""Validate build-loop evidence records; never execute or certify app tests."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / 'docs/build-loop/ACCEPTANCE.json'
EXPECTED = ({f'G0-{x}' for x in 'ABCDEF'} |
            {f'T{x:02}' for x in range(1, 39)} |
            {f'U{x:02}' for x in range(1, 13)} |
            {f'P{x:02}' for x in range(1, 9)})
EXTERNAL = {'P06', 'P07', 'P08'}
STATUSES = {'NOT_RUN', 'PASS', 'FAIL', 'BLOCKED'}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def local_file(value):
    if not nonempty(value) or Path(value).is_absolute():
        raise ValueError(f'Expected project-relative file: {value!r}')
    path = (ROOT / value).resolve()
    if ROOT not in path.parents or not path.is_file():
        raise ValueError(f'Missing or outside-project file: {value!r}')
    return path


def validate(data):
    if data.get('schema_version') != 1 or data.get('theme') != 'graphite':
        raise ValueError('Expected schema_version 1 and theme graphite')
    rows = data.get('checks')
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise ValueError('checks must be a list of records')
    ids = [r.get('id') for r in rows]
    if any(not isinstance(x, str) for x in ids):
        raise ValueError('Every check needs a string id')
    if len(ids) != len(set(ids)) or set(ids) != EXPECTED:
        raise ValueError('Check ids must match all G0-A..F, T01..38, U01..12, P01..08 exactly')
    for row in rows:
        cid = row['id']
        if row.get('scope') != ('external' if cid in EXTERNAL else 'local'):
            raise ValueError(f'{cid}: scope cannot be changed to bypass readiness')
        if not nonempty(row.get('title')) or row.get('status') not in STATUSES:
            raise ValueError(f'{cid}: invalid title/status')
        local_file(row.get('source'))
        evidence = row.get('evidence')
        if not isinstance(evidence, list) or not isinstance(row.get('defects'), list):
            raise ValueError(f'{cid}: evidence and defects must be lists')
        for ref in evidence:
            if local_file(ref).stat().st_size == 0:
                raise ValueError(f'{cid}: empty evidence file {ref}')
        if row['status'] == 'PASS':
            for field in ('revision', 'verified_at', 'procedure', 'expected', 'observed', 'verifier'):
                if not nonempty(row.get(field)):
                    raise ValueError(f'{cid}: PASS requires {field}')
            if not evidence or row['defects']:
                raise ValueError(f'{cid}: PASS requires evidence and no unresolved defects')
        elif row['status'] in {'FAIL', 'BLOCKED'} and not nonempty(row.get('observed')):
            raise ValueError(f'{cid}: failure/blocker needs an observed explanation')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, default=DEFAULT)
    parser.add_argument('--ready', action='store_true', help='Require complete local candidate records')
    args = parser.parse_args()
    try:
        data = json.loads(args.ledger.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('Ledger must be an object')
        rows = validate(data)
    except (OSError, ValueError, TypeError) as exc:
        print(f'INVALID LEDGER: {exc}')
        return 1
    counts = Counter(row['status'] for row in rows)
    print(f'VALID RECORD STRUCTURE: {len(rows)} checks; {dict(counts)}')
    print('Records only. No application, model, UI or publishing tests were executed.')
    if args.ready:
        candidate = data.get('candidate_revision')
        pending = [r['id'] for r in rows if r['scope'] == 'local' and r['status'] != 'PASS']
        stale = [r['id'] for r in rows if r['scope'] == 'local' and r['status'] == 'PASS'
                 and r['revision'] != candidate]
        if not nonempty(candidate) or pending or stale:
            print(f'NOT READY: candidate={candidate!r}; unpassed={pending}; other_revision={stale}')
            return 2
        print('LOCAL RECORD GATE SATISFIED. Independent evidence review is still required.')
        print('External publication states:', {r['id']: r['status'] for r in rows if r['scope'] == 'external'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
