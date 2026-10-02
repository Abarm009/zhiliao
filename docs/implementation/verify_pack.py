#!/usr/bin/env python3
"""Offline design checks only; no application or live integration is tested."""
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


def main():
    required = ['README.md', 'ARCHITECTURE.html', 'schema.sql', 'openapi.json']
    required += ['00_DECISIONS.md', '01_REQUIREMENTS.md', '02_ARCHITECTURE.md',
                 '03_TECH_STACK.md', '04_DATA_API.md', '05_IMPLEMENTATION_ACCEPTANCE.md',
                 '06_OFFICIAL_COMPLIANCE.md', '07_REVISION_20260926.md',
                 '08_REUSE_MIGRATION.md', '09_AGENT_HARNESS.md', '10_UI_UX_SPEC.md', '11_COURSE1_BASELINE_REVIEW.md', '12_DELIVERY_PLAN_20261009.md', '13_APP_HUB_SUBMISSION_REVIEW.md', '14_COURSE2_LATEST_GUIDE_REVIEW.md', '15_BUILD_VERIFY_LOOP.md', '../build-loop/README.md', '../build-loop/START_PROMPT.md', '../build-loop/ITERATION_TEMPLATE.md', '../build-loop/ACCEPTANCE.json']
    for name in ['system', 'workflow', 'execution', 'deployment', 'data', 'agentic-loop']:
        required += ['diagrams/' + name + ext for ext in ['.svg', '.mmd']]
    for name in required:
        assert (ROOT / name).is_file(), name
    links = 0
    for p in list(ROOT.glob('*.md')) + [ROOT / 'ARCHITECTURE.html']:
        content = p.read_text(encoding='utf-8')
        targets = re.findall(r'\]\(([^\s)]+)\)', content) if p.suffix == '.md' else re.findall(r'href="([^"]+)"', content)
        for target in targets:
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            assert (p.parent / unquote(url.path)).exists(), (p.name, target)
            links += 1
    for p in (ROOT / 'diagrams').glob('*.svg'):
        svg = ET.parse(p).getroot()
        assert svg.tag.endswith('svg') and svg.get('viewBox'), p.name
    html = (ROOT / 'ARCHITECTURE.html').read_text(encoding='utf-8')
    assert html.count('<svg ') == 6
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids)), 'Duplicate HTML/SVG IDs'

    spec = json.loads((ROOT / 'openapi.json').read_text(encoding='utf-8'))
    refs = []
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == '$ref':
                    assert item.startswith('#/'), item
                    node = spec
                    for part in item[2:].split('/'):
                        node = node[part.replace('~1', '/').replace('~0', '~')]
                    refs.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(spec)
    methods = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}
    ops = [op for route in spec['paths'].values() for method, op in route.items() if method in methods]
    assert len(ops) == 24
    assert len({op['operationId'] for op in ops}) == len(ops)
    schemas = spec['components']['schemas']
    commands = schemas['TaskCommand']['discriminator']['mapping']
    assert len(commands) == 14
    doc = (ROOT / '04_DATA_API.md').read_text(encoding='utf-8')
    for name, ref in commands.items():
        command = schemas[ref.rsplit('/', 1)[1]]
        assert command['properties']['type']['const'] == name
        assert command['additionalProperties'] is False
        assert 'expected_version' in command['required'] and name in doc
    assert len(schemas['TaskStatus']['enum']) == 8

    db = sqlite3.connect(':memory:')
    db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
    db.execute("INSERT INTO repair_orgs VALUES('o','Example')")
    for project in ['p', 'q']:
        db.execute('INSERT INTO repair_projects(id,org_id,name) VALUES(?,?,?)', (project, 'o', project))
        db.execute('INSERT INTO repair_spaces(id,project_id,code,name,source) VALUES(?,?,?,?,?)', ('s'+project, project, 'S', 'Space', 'DEMO'))
    for user in ['r', 't']:
        db.execute('INSERT INTO repair_users(id,org_id,username,display_name,password_hash) VALUES(?,?,?,?,?)', (user, 'o', user, user, 'fixture-only'))
    db.execute("INSERT INTO repair_assets(id,project_id,asset_code,display_name,category,source,captured_at_ms) VALUES('a','p','A','Asset','HVAC','DEMO',1)")
    for number, project in [('1', 'p'), ('2', 'q'), ('3', 'p')]:
        db.execute("INSERT INTO repair_tasks(id,task_no,project_id,reporter_id,status,raw_text,created_at_ms,updated_at_ms) VALUES(?,?,?,'r','OPEN','Example',1,1)", (number, 'T'+number, project))
    checks = []
    def rejected(label, sql, args=()):
        try:
            db.execute(sql, args)
        except sqlite3.IntegrityError:
            checks.append(label)
        else:
            raise AssertionError('Constraint missing: ' + label)
    def appointment(id_, task, start, end, status):
        return (id_, task, 't', start, end, 99, status, 't', 'r', 1, 1)
    ap_sql = ('INSERT INTO repair_appointments(id,task_id,technician_id,start_at_ms,end_at_ms,expires_at_ms,status,proposed_by,confirmed_by,created_at_ms,updated_at_ms) VALUES(?,?,?,?,?,?,?,?,?,?,?)')
    db.execute(ap_sql, appointment('a1', '1', 100, 200, 'CONFIRMED'))
    rejected('cross-project technician overlap', ap_sql, appointment('a2', '2', 150, 250, 'CONFIRMED'))
    db.execute(ap_sql, appointment('a3', '2', 200, 300, 'CONFIRMED'))
    checks.append('adjacent intervals allowed')
    rejected('one confirmed appointment per task', ap_sql, appointment('a4', '1', 400, 500, 'CONFIRMED'))
    db.execute(ap_sql, appointment('a5', '3', 300, 400, 'PROPOSED'))
    rejected('one proposal per task', ap_sql, appointment('a6', '3', 500, 600, 'PROPOSED'))
    rejected('overlap on update', "UPDATE repair_appointments SET status='CONFIRMED',start_at_ms=199 WHERE id='a5'")
    rejected('cross-project asset binding', "UPDATE repair_tasks SET asset_id='a' WHERE id='2'")
    rejected('unsupported external authority', "UPDATE repair_projects SET authority_mode='EXTERNAL' WHERE id='p'")
    action_sql = "INSERT INTO repair_actions(id,org_id,actor_id,actor_kind,idempotency_key,request_hash,command_type,status,result_json,created_at_ms) VALUES(?,'o','r','USER','same-key','hash','accept_task','SUCCEEDED','{}',1)"
    db.execute(action_sql, ('x1',))
    rejected('actor idempotency uniqueness', action_sql, ('x2',))
    db.execute("INSERT INTO repair_attachments VALUES('f','2','r','file','sample.png','image/png',10,'sha','READY',1)")
    db.execute("INSERT INTO repair_completions VALUES('c','1','t','Done','UNKNOWN',1)")
    rejected('cross-task completion evidence', "INSERT INTO repair_completion_attachments VALUES('c','f','1')")
    rejected('manager acceptance requires reason', "INSERT INTO repair_acceptances VALUES('v','1','c','r','ACCEPTED',1,NULL,1)")
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    tables = db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name LIKE 'repair_%'").fetchone()[0]
    db.close()
    cases = (ROOT / '05_IMPLEMENTATION_ACCEPTANCE.md').read_text(encoding='utf-8') + (ROOT / '09_AGENT_HARNESS.md').read_text(encoding='utf-8')
    case_ids = re.findall(r'^\|T(\d{2})(?:\|| )', cases, flags=re.M)
    assert sorted(case_ids) == ['%02d' % i for i in range(1, 39)], 'Acceptance cases must be exactly T01-T38'
    print('PASS: %s files, %s local links, 6 SVGs and embedded diagrams; T01-T38 declared (not run)' % (len(required), links))
    print('PASS: 24 operations, 14 commands, %s schemas, %s resolved references' % (len(schemas), len(refs)))
    print('PASS: %s SQL tables; %s constraint scenarios' % (tables, len(checks)))
    for check in checks:
        print('  - ' + check)
    print('Design checks only. Application, concurrency, model and host tests NOT RUN.')


if __name__ == '__main__':
    main()
