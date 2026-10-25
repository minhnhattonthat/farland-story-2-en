import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
def test_rom_matches_sha1():
    check_rom.check()  # sys.exit on mismatch fails the test


def test_tools_import():
    import bps, romdiff, tbl  # noqa: F401  copied from the skill so a clone builds without it
