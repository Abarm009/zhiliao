"""Run inherited offline tests against this copy, with temporary runtime data."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="wagent-migration-test-") as tmp:
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(ROOT / "backend" / "src"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "WAGENT_OPS_DB": str(Path(tmp) / "ops.db"),
            "WAGENT_KG_DATA": str(Path(tmp) / "kg.json"),
            "WAGENT_SESSIONS_DIR": str(Path(tmp) / "sessions"),
            "WAGENT_EMBEDDING": "local",
            "WAGENT_OPS_SIMSEED": "0",
            "LLM_API_KEY": "",
            "OPENAI_API_KEY": "",
        })
        # Confirm editable installs cannot silently redirect verification to the old copy.
        probe = subprocess.run(
            [sys.executable, "-c", "import wagent_backend; print(wagent_backend.__file__)"],
            cwd=ROOT / "backend", env=env, text=True, capture_output=True, check=True,
        )
        imported = Path(probe.stdout.strip()).resolve()
        if not imported.is_relative_to(ROOT / "backend" / "src"):
            raise RuntimeError(f"Imported unexpected backend: {imported}")
        print(f"Testing copied source: {imported}", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
            cwd=ROOT / "backend", env=env,
        )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
