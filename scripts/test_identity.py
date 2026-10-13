#!/usr/bin/env python3
"""Execute exact production Splash guards in the local Makepad VM + actual jailed fs.

This is a headless contract probe, never a launcher/UI acceptance test.
All credentials below are deterministic synthetic test fixtures, not Abram's tokens.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from manage_identity import PEOPLE, ROUNDS, validate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime/identity/evidence"
VM = OUT / "vm/target/release/identity-vm-probe"


def function(source: str, name: str) -> str:
    m = re.search(r"^fn " + re.escape(name) + r"\(", source, re.M)
    if not m:
        raise ValueError("missing production function " + name)
    start = source.index("{", m.start())
    depth, quoted, escape, comment = 0, False, False, False
    for i in range(start, len(source)):
        c = source[i]
        if comment:
            if c == "\n":
                comment = False
            continue
        if quoted:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                quoted = False
            continue
        if c == '"':
            quoted = True
        elif source[i:i + 2] == "//":
            comment = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[m.start():i + 1]
    raise ValueError("unterminated production function")


def block(source: str, name: str) -> str:
    return source[source.index("// " + name + "_BEGIN"):source.index("// " + name + "_END") + len("// " + name + "_END")]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = (ROOT / "app/bundle/main.splash").read_text()
    crypto = block(source, "IDENTITY_CRYPTO")
    auth = block(source, "IDENTITY_AUTH")
    assert crypto == (ROOT / "scripts/identity_crypto.splash").read_text().strip()
    assert auth == (ROOT / "scripts/identity_auth.splash").read_text().strip()
    assert "USERS" not in re.sub(r"//[^\n]*", "", source)
    # The only remaining state actor reference explicitly discards that untrusted field.
    assert source.count("STATE.actor") == 1 and "STATE.actor=nil" in source
    bound = function(source, "runCommandBound")
    assert bound.index("authorizeCommand") < bound.index("_acquireTaskLock") < bound.index("RECEIPTS.len")
    now = 1800000000000
    data = {"schema": 2, "registry_kind": "local_accounts", "accounts": []}
    tokens = {}
    for i, (ident, name, roles, skills) in enumerate(PEOPLE):
        token, salt = bytes([i + 1]) * 32, bytes([i + 21]) * 16
        tokens[ident] = token.hex()
        data["accounts"].append({"id": ident, "name": name, "roles": roles, "skills": skills,
                                 "enabled": True, "revoked_at": 0, "expires_at": now + 86400000,
                                 "credential_epoch": 1,
                                 "kdf": {"scheme": "pbkdf2-sha256-token-v1", "iterations": ROUNDS,
                                         "salt": salt.hex(), "hash": hashlib.pbkdf2_hmac("sha256", token, salt, ROUNDS).hex()}})
    validate(data)
    mutations = {"baseline": data}
    for case in ("revoked", "expired", "removed", "role_changed", "epoch", "duplicate"):
        d = copy.deepcopy(data)
        for p in d["accounts"]:
            if p["id"] in ("u-reporter-1", "u-reporter-2"):
                if case == "revoked": p["revoked_at"] = now - 1
                if case == "expired": p["expires_at"] = now - 1
                if case == "removed": p["roles"] = {}
                if case == "role_changed": p["roles"] = {k: ["TECHNICIAN"] for k in p["roles"]}
                if case == "epoch": p["credential_epoch"] = 2
        if case == "duplicate": d["accounts"].append(copy.deepcopy(d["accounts"][0]))
        mutations[case] = d
    mutations["malformed"] = {"schema": 2, "registry_kind": "local_accounts"}
    common = '''use mod.std.assert
let fs=mod.fs
let probe=mod.probe
let STATE={project:"prj-A",actor:"u-manager",selectedIdx:0,status:"",demo_view_as:""}
let S_DRAFT="DRAFT"; let S_OPEN="OPEN"
let LAST_KEY="saved-action"; let LOCK_ATTEMPTS=0
fn nowMs(){ return 1800000000000 }
fn _acquireTaskLock(){ LOCK_ATTEMPTS=LOCK_ATTEMPTS+1; return false }
fn _releaseTaskLock(){}
'''
    helpers = ["hasRole", "skillOk", "isReporter", "isAssignee", "isManager", "visible",
               "authorizeTask", "saveState", "fail", "setActorM2", "runCommandBound", "receiptFor",
               "m6_history_render", "m6_summary_lines", "m6_history_for_task_count", "commitBound"]
    # authorizeTask already lives in the exact auth block.
    common += crypto + "\n" + auth + "\n" + "\n".join(function(source, n) for n in helpers if n != "authorizeTask")
    common += '\nfn findTaskById(id){ for t in TASKS { if t.id == id { return t } }; return nil }\n'
    results = []
    processes = []
    for ident, project in (("u-reporter-1", "prj-A"), ("u-reporter-2", "prj-B")):
        jail = OUT / ("session-" + ident)
        (jail / "identity").mkdir(parents=True, exist_ok=True)
        (jail / "fixtures").mkdir(exist_ok=True)
        for case, d in mutations.items():
            (jail / f"fixtures/{case}.json").write_text(json.dumps(d, ensure_ascii=False))
        target = jail / "identity/accounts.json"
        if target.exists(): target.unlink()
        target.write_text(json.dumps(data, ensure_ascii=False))
        target.chmod(0o400)
        task = {"id": "test-" + ident, "project": project, "reporter": ident,
                "assignee": None, "status": "DRAFT", "category": "HVAC_NOT_COOLING", "version": 0}
        receipt = {"actor": ident, "key": "saved-action", "fp": "saved-fp", "task_id": task["id"],
                   "command": "confirmDraft", "status": "final", "action_id": "synthetic-action"}
        facts = {"tasks.json": [task], "actions.jsonl": [receipt], "events.jsonl": []}
        for file, contents in facts.items():
            (jail / file).write_text(json.dumps(contents))
        (jail / "state.json").write_text(json.dumps({"actor": "u-manager", "project": project}))
        before = {f: hashlib.sha256((jail / f).read_bytes()).hexdigest() for f in facts}
        code = common + '\nlet TASKS=fs.read("tasks.json").parse_json()\nlet RECEIPTS=fs.read("actions.jsonl").parse_json()\n'
        code += 'assert(loadViewState())\nSTATE.selectedIdx=0\nlet t=TASKS[0]\n'
        code += 'assert(sessionActor()=="")\nassert(!authorizeTask(t))\n'
        code += f'assert(authBegin("{ident}","{tokens[ident]}"))\n'
        code += 'while AUTH_JOB != nil { authStep() }\n'
        code += f'assert(sessionActor()=="{ident}")\nassert(getMe().id=="{ident}")\n'
        code += '''assert(authorizeCommand("confirmDraft",t,{}))
assert(receiptFor("saved-action","saved-fp").kind=="hit")
assert(!authorizeCommand("assignTask",t,{assignee:"u-tech-1"}))
fs.write("state.json",{actor:"u-manager",project:STATE.project,selectedIdx:0,status:"",subject:"u-manager",session:{subject:"u-manager"}}.to_json())
assert(loadViewState())
setActorM2("u-manager")
assert(!authorizeCommand("assignTask",t,{assignee:"u-tech-1"}))
assert(getMe().id==t.reporter)
fs.write("/absolute-probe.json","inside-jail")
assert(fs.read("absolute-probe.json")=="inside-jail")
let escaped=false
try { fs.read("../outside.json"); escaped=true } catch { false }
assert(!escaped)
let secret_write=false
try { fs.write("identity/accounts.json","forged") ; secret_write=true } catch { false }
assert(!secret_write)
'''
        for case in ("revoked", "expired", "removed", "role_changed", "epoch", "malformed", "duplicate"):
            code += f'probe.replace_authority("{case}")\n'
            code += '''assert(!runCommandBound("confirmDraft",t,{},0))
assert(receiptFor("saved-action","saved-fp").kind=="denied")
assert(m6_history_render(t).kind=="denied")
assert(m6_history_for_task_count(t)==0)
assert(m6_summary_lines(t)[0]=="身份或项目角色无效；拒绝查询")
assert(!commitBound(t,0,"confirmDraft",{}))
assert(LOCK_ATTEMPTS==0)
probe.replace_authority("baseline")
'''
        code += '''SESSION.expires_at=nowMs()-1
assert(!runCommandBound("confirmDraft",t,{},0))
assert(receiptFor("saved-action","saved-fp").kind=="denied")
assert(LOCK_ATTEMPTS==0)
'''
        code += f'''authLogout()
AUTH_RETRY_AT=0
assert(authBegin("{ident}","{'ff' * 32}"))
while AUTH_JOB != nil {{ authStep() }}
assert(sessionActor()=="")
assert(!runCommandBound("confirmDraft",t,{{}},0))
assert(receiptFor("saved-action","saved-fp").kind=="denied")
assert(LOCK_ATTEMPTS==0)
true
'''
        script = OUT / ("probe-" + ident + ".splash")
        script.write_text(code)
        log_path = OUT / ("probe-" + ident + ".log")
        log = log_path.open("w")
        process = subprocess.Popen([str(VM), str(script), str(jail)], stdout=log, stderr=log)
        processes.append((ident, process, log, jail, before, log_path))
    # The other three account configurations also log in through the exact KDF/session code.
    for ident, category, command, params in (
        ("u-tech-1", "HVAC_NOT_COOLING", "acceptTask", {}),
        ("u-tech-2", "ELECTRICAL", "acceptTask", {}),
        ("u-manager", "HVAC_NOT_COOLING", "assignTask", {"assignee": "u-tech-1"}),
    ):
        jail = OUT / ("session-" + ident)
        (jail / "identity").mkdir(parents=True, exist_ok=True)
        target = jail / "identity/accounts.json"
        if target.exists(): target.unlink()
        target.write_text(json.dumps(data, ensure_ascii=False)); target.chmod(0o400)
        task = {"id": "test-" + ident, "project": "prj-A", "reporter": "u-reporter-1",
                "assignee": None, "status": "OPEN", "category": category, "version": 1}
        facts = {"tasks.json": [task], "actions.jsonl": [], "events.jsonl": []}
        for file, contents in facts.items(): (jail / file).write_text(json.dumps(contents))
        before = {f: hashlib.sha256((jail / f).read_bytes()).hexdigest() for f in facts}
        code = common + '\nlet TASKS=fs.read("tasks.json").parse_json()\nlet RECEIPTS=[]\nlet t=TASKS[0]\n'
        code += f'assert(authBegin("{ident}","{tokens[ident]}"))\nwhile AUTH_JOB != nil {{ authStep() }}\n'
        code += f'assert(getMe().id=="{ident}")\nassert(authorizeCommand("{command}",t,{json.dumps(params)}))\n'
        code += 'STATE.actor="u-reporter-2"\nassert(getMe().id=="' + ident + '")\n'
        code += 'assert(!authorizeCommand("confirmDraft",t,{}))\nauthLogout()\nassert(!authorizeTask(t))\ntrue\n'
        script = OUT / ("probe-" + ident + ".splash"); script.write_text(code)
        log_path = OUT / ("probe-" + ident + ".log"); log = log_path.open("w")
        process = subprocess.Popen([str(VM), str(script), str(jail)], stdout=log, stderr=log)
        processes.append((ident, process, log, jail, before, log_path))
    for ident, process, log, jail, before, log_path in processes:
        try:
            rc = process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(); raise
        finally:
            log.close()
        after = {f: hashlib.sha256((jail / f).read_bytes()).hexdigest() for f in before}
        results.append({"account_fixture": ident, "pid": process.pid, "rc": rc,
                        "facts_unchanged": before == after, "before": before, "after": after,
                        "log": str(log_path.relative_to(ROOT)),
                        "cases": (["independent_login", "wrong_role", "state_actor_spoof", "view_switch",
                                  "read_only_authority", "revoked", "expired", "project_removed", "role_changed",
                                  "credential_epoch_changed", "malformed_authority", "duplicate_authority", "wrong_token", "session_expired", "jailed_path_resolution"]
                                  if ident.startswith("u-reporter") else ["independent_login", "expected_role_command", "wrong_role", "state_actor_spoof", "logout_denies"])})
    (OUT / "contract-results.json").write_text(json.dumps({"scope": "actual Splash functions and copied host jailed fs; headless VM, not launcher/UI",
                                                           "native_launcher": "BLOCKED", "sessions": results}, indent=2))
    print(json.dumps([{"session": r["account_fixture"], "rc": r["rc"], "facts_unchanged": r["facts_unchanged"]} for r in results]))
    if any(r["rc"] != 0 or not r["facts_unchanged"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
