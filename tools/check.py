"""check.py: the one-command check the pre-commit hook runs (tests + text lint). Exit non-zero on any failure.

    python -X utf8 tools/check.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.exit(subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT).returncode)
