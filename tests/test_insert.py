"""Phase 7: the English build passes the ROM checks (every changed byte is a logged write against the clean dump or
inside an assembler range of data/romdiff.txt), writes every translated string, and the whole-script lint is clean."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import hookcheck  # noqa: E402
import lint  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file() or not build.ASAR.is_file(), reason="ROM or asar absent")


@pytest.fixture(scope="module")
def english():
    rom, out, _, _ = build.build()
    return rom, out, list(build.WRITES)


@needs_rom
def test_romdiff_clean(english):
    assert build.romcheck(*english) == []


@needs_rom
def test_romdiff_catches_stray_and_stale_writes(english):
    rom, out, log = english
    stray = bytearray(out)
    stray[0x8000] ^= 0xFF  # bank $C0 code, no write and no range
    assert build.romcheck(rom, bytes(stray), log)
    off, orig, new, by = log[0]
    stale = [(off, bytes(b ^ 0xFF for b in orig), new, by)] + log[1:]
    assert any("expects orig" in x for x in build.romcheck(rom, out, stale))


@needs_rom
def test_every_translated_string_written(english):
    written = {by for _, _, _, by in english[2]}
    assert [e["id"] for e in build.load_script() if e["en"] and e["id"] not in written] == []


def test_lint_clean():
    assert lint.lint() == []


@needs_rom
def test_no_branch_into_a_hook():
    rom = build.ROM.read_bytes()
    assert [h for lo, hi in hookcheck.spans() for h in hookcheck.hits(rom, lo, hi)] == []
