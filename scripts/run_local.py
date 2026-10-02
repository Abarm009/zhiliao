"""Run the copied backend with project-local state, regardless of cwd."""
from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8711)
    args = parser.parse_args()
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    # Deliberately override inherited paths so the old project's state is untouched.
    os.environ.update({
        "WAGENT_OPS_DB": str(runtime / "ops.db"),
        "WAGENT_KG_DATA": str(runtime / "kg.json"),
        "WAGENT_SESSIONS_DIR": str(runtime / "sessions"),
    })
    os.environ.setdefault("WAGENT_EMBEDDING", "local")
    os.environ.setdefault("WAGENT_OPS_SIMSEED", "0")
    sys.path.insert(0, str(ROOT / "backend" / "src"))
    import uvicorn
    from wagent_backend.web.app import app
    print(f"Migration baseline only. Runtime: {runtime}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
