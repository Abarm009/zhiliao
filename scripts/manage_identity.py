#!/usr/bin/env python3
"""Local account provisioning and fail-closed sync. No network, no secret stdout."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
import secrets
import stat
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "runtime/identity"
ACCOUNTS = BASE / "accounts.json"
CREDENTIALS = BASE / "CREDENTIALS_FOR_ABRAM.md"
INSTALLS = BASE / "installations.json"
ROUNDS = 4096
PEOPLE = [
    ("u-reporter-1", "报修人一", {"prj-A": ["REPORTER"]}, []),
    ("u-reporter-2", "报修人二", {"prj-B": ["REPORTER"]}, []),
    ("u-tech-1", "技工甲（HVAC）", {"prj-A": ["TECHNICIAN"]}, ["HVAC"]),
    ("u-tech-2", "技工乙（电气）", {"prj-A": ["TECHNICIAN"], "prj-B": ["TECHNICIAN"]}, ["ELECTRICAL"]),
    ("u-manager", "经理丙", {"prj-A": ["MANAGER"]}, []),
]


def confined(path: Path) -> Path:
    path = path.absolute()
    if path != path.resolve() or not path.is_relative_to(ROOT / "runtime"):
        raise ValueError("identity files must be non-symlink paths within project runtime")
    return path


def atomic(path: Path, data: bytes, mode: int = 0o400) -> None:
    confined(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix=".identity-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def validate(data: dict) -> None:
    if data.get("schema") != 2 or data.get("registry_kind") != "local_accounts":
        raise ValueError("invalid authority schema")
    if len(data["accounts"]) != 5 or {p["id"] for p in data["accounts"]} != {p[0] for p in PEOPLE}:
        raise ValueError("authority must contain the five provisioned accounts")
    for p in data["accounts"]:
        if type(p["enabled"]) is not bool:
            raise ValueError("invalid enabled flag")
        for field in ("expires_at", "revoked_at", "credential_epoch"):
            if type(p[field]) is not int or p[field] < 0:
                raise ValueError("invalid lifecycle field")
        if p["credential_epoch"] < 1:
            raise ValueError("invalid credential epoch")
        for project, roles in p["roles"].items():
            if project not in ("prj-A", "prj-B") or not isinstance(roles, list):
                raise ValueError("invalid membership")
            if any(role not in ("REPORTER", "TECHNICIAN", "MANAGER") for role in roles):
                raise ValueError("invalid role")
        k = p["kdf"]
        if k["scheme"] != "pbkdf2-sha256-token-v1" or k["iterations"] != ROUNDS:
            raise ValueError("invalid KDF")
        for field, length in (("salt", 16), ("hash", 32)):
            if len(bytes.fromhex(k[field])) != length or k[field] != k[field].lower():
                raise ValueError("invalid KDF encoding")


def registered() -> list[Path]:
    if not INSTALLS.exists():
        return []
    return [confined(Path(s)) for s in json.loads(INSTALLS.read_text())["data_dirs"]]


def publish(data: dict, dirs: list[Path]) -> None:
    validate(data)
    paths = [confined(d / "identity/accounts.json") for d in dirs]
    # Revoke old grants in ALL installed jails first. A interrupted sync cannot
    # leave a partially updated installation silently carrying an old authority.
    for path in paths:
        atomic(path, encode({"schema": 0, "registry_kind": "sync_in_progress"}))
    payload = encode(data)
    atomic(ACCOUNTS, payload)
    for path in paths:
        atomic(path, payload)
        if path.read_bytes() != payload or stat.S_IMODE(path.stat().st_mode) != 0o400:
            raise OSError("authority readback mismatch")
    atomic(INSTALLS, encode({"schema": 1, "data_dirs": [str(d) for d in dirs]}), 0o600)


def provision() -> None:
    if ACCOUNTS.exists() or CREDENTIALS.exists() or INSTALLS.exists():
        raise ValueError("already provisioned; refusing to regenerate credentials")
    now = int(time.time() * 1000)
    accounts = []
    lines = ["# OctoSense 初始凭据 · 仅供 Abram", "", "禁止入库、上传、截图或复制到日志/报告。令牌只适用于本地报修应用。", "",
             "原生宿主登录目前 BLOCKED；详见本轮 M2 报告。创建账号不代表已原生登录。", "",
             "|账号 ID|名称|初始令牌|", "|---|---|---|"]
    for ident, name, roles, skills in PEOPLE:
        token = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        accounts.append({"id": ident, "name": name, "roles": roles, "skills": skills,
                         "enabled": True, "revoked_at": 0, "expires_at": now + 365 * 86400000,
                         "credential_epoch": 1,
                         "kdf": {"scheme": "pbkdf2-sha256-token-v1", "iterations": ROUNDS,
                                 "salt": salt.hex(), "hash": hashlib.pbkdf2_hmac("sha256", token, salt, ROUNDS).hex()}})
        lines.append(f"|{ident}|{name}|{token.hex()}|")
    # Exclusive creation, mode 600 from the first byte; never print this value.
    fd = os.open(CREDENTIALS, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as out:
        os.fchmod(out.fileno(), 0o600)
        out.write("\n".join(lines) + "\n")
        out.flush()
        os.fsync(out.fileno())
    data = {"schema": 2, "registry_kind": "local_accounts", "created_at": now, "accounts": accounts}
    publish(data, [])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("provision")
    install = sub.add_parser("install")
    install.add_argument("--data-dir", required=True, type=Path)
    sub.add_parser("sync")
    change = sub.add_parser("change")
    change.add_argument("id", choices=[p[0] for p in PEOPLE])
    ops = change.add_mutually_exclusive_group(required=True)
    ops.add_argument("--revoke", action="store_true")
    ops.add_argument("--expires-at-ms", type=int)
    ops.add_argument("--remove-project", choices=["prj-A", "prj-B"])
    ops.add_argument("--disable", action="store_true")
    args = parser.parse_args()
    confined(BASE)
    BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(BASE, 0o700)
    lock = os.open(BASE / ".admin.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.command == "provision":
            provision()
            print("Created five accounts; credentials saved privately (mode 600).")
            return
        data = json.loads(ACCOUNTS.read_text())
        validate(data)
        dirs = registered()
        if args.command == "install":
            target = confined(args.data_dir)
            if target not in dirs:
                dirs.append(target)
        if args.command == "change":
            p = next(p for p in data["accounts"] if p["id"] == args.id)
            if args.revoke:
                p["revoked_at"] = int(time.time() * 1000)
            if args.expires_at_ms is not None:
                p["expires_at"] = args.expires_at_ms
            if args.remove_project:
                p["roles"].pop(args.remove_project, None)
            if args.disable:
                p["enabled"] = False
        publish(data, dirs)
        print(f"Authority synchronized and read back in {len(dirs)} local data directories.")
    finally:
        os.close(lock)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError):
        # Do not include parsed data, command content or exception values.
        raise SystemExit("Identity operation failed; no success claimed. Check authority/install paths locally.")
