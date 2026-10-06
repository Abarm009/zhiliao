"""Start the OctoSense repair app locally: domain backend + browser demo.

What this starts (both bind 127.0.0.1 only):
  1. `octosense_backend.api:make_app` — the SQLite domain core and
     `/api/octosense/v1/*` (this is the app's business logic).
  2. `app/demo-web/server.py` — the local HTML demo, a thin reverse proxy to 1.

What this does NOT start: the OctoSense-native app. That is the octoscript
bundle in `app/bundle/`, run by the host binary:

    MAKEPAD_REMOTE=<port> \\
    runtime/native-build/OctoSense-App-Hub/target/release/card-host \\
      --bundle app/bundle --app-data runtime/live/<dir> --allow-unsigned --stamp

Previously this script launched `wagent_backend.web.app`, i.e. the migrated
legacy WAgent backend, so the README's "移动后运行" step showed the wrong
application. The OctoSense entry point is the one above plus this one.

Usage:
    python3 scripts/run_local.py                    # backend 8711 + demo 8712
    python3 scripts/run_local.py --no-web           # backend only
    python3 scripts/run_local.py --runtime runtime/demo
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = ROOT / "backend" / "src"
DEMO_DIR = ROOT / "app" / "demo-web"
VENV_PY = ROOT / "backend" / ".venv" / "bin" / "python"
WINDOWS_VENV_PY = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"


def interpreter() -> str:
    """Prefer the project venv; fall back to the running interpreter."""
    for cand in (VENV_PY, WINDOWS_VENV_PY):
        if cand.exists():
            return str(cand)
    return sys.executable


def prepare_runtime(runtime: Path) -> None:
    """Pin every state path under this project's runtime/ (never the old one)."""
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ["OCTOSENSE_DB"] = os.environ.get(
        "OCTOSENSE_DB", str(runtime / "octosense.db"))
    os.environ["OCTOSENSE_EVIDENCE_ROOT"] = os.environ.get(
        "OCTOSENSE_EVIDENCE_ROOT", str(runtime / "evidence"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8711,
                        help="domain backend port (default 8711)")
    parser.add_argument("--web-port", type=int, default=8712,
                        help="browser demo port (default 8712)")
    parser.add_argument("--runtime", default="runtime",
                        help="runtime directory for db + evidence (default runtime/)")
    parser.add_argument("--no-web", action="store_true",
                        help="start only the domain backend")
    args = parser.parse_args()

    runtime = (ROOT / args.runtime).resolve() \
        if not Path(args.runtime).is_absolute() else Path(args.runtime)
    prepare_runtime(runtime)
    py = interpreter()

    print(f"OctoSense runtime : {runtime}")
    print(f"  db              : {os.environ['OCTOSENSE_DB']}")
    print(f"  evidence        : {os.environ['OCTOSENSE_EVIDENCE_ROOT']}")
    print(f"  backend         : http://127.0.0.1:{args.port}/api/octosense/v1/health")

    if args.no_web:
        return _run_backend(py, args.port)

    web_env = dict(os.environ)
    web_env["OCTOSENSE_DEMO_PORT"] = str(args.web_port)
    web_env["OCTOSENSE_BACKEND_BASE"] = f"http://127.0.0.1:{args.port}"
    web = subprocess.Popen(
        [py, "-m", "uvicorn", "server:app", "--app-dir", str(DEMO_DIR),
         "--host", "127.0.0.1", "--port", str(args.web_port)],
        cwd=str(ROOT), env=web_env)
    print(f"  browser demo    : http://127.0.0.1:{args.web_port}/static/workbench.html")
    print("(Ctrl-C stops both; the demo exits when the backend does)")
    try:
        return _run_backend(py, args.port)
    finally:
        web.terminate()


def _run_backend(py: str, port: int) -> int:
    cmd = [py, "-m", "uvicorn", "--app-dir", str(BACKEND_SRC),
           "octosense_backend.api:make_app", "--factory",
           "--host", "127.0.0.1", "--port", str(port)]
    print("  launching       :", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
