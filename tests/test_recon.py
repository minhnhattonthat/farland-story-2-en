"""Recon facts that later phases build on (docs/re/): table, LZ codec, fonts."""
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def table():
    return Table.load(ROOT / "tbl" / "jp.tbl")


def test_table_values_unique():
    dup = [v for v, n in Counter(table().dec.values()).items() if n > 1]
    assert not dup


def test_lz_roundtrip():
    lz.selftest()


@needs_rom
def test_table_covers_every_glyph():
    rom, t = ROM.read_bytes(), table()
    missing = [hex(c) for c in range(0x32A) if any(rom[0x41000 + c * 32:0x41020 + c * 32])
               and c.to_bytes(2, "little") not in t.dec]
    assert not missing


@needs_rom
def test_opening_narration_decodes_and_roundtrips():
    rom, t = ROM.read_bytes(), table()
    text, used = t.decode(rom, 0x483D9)
    assert text.startswith("{full}アークが{nl}フェルサリアの王となって２０年{wait}{nl}世界は大きく変わりはじめていた")
    assert t.encode(text) == rom[0x483D9:0x483D9 + used]


@needs_rom
def test_lz_title_block():
    rom = ROM.read_bytes()
    data, size = lz.decompress(rom, 0x6321)
    assert (len(data), size) == (8192, 6584)
    assert lz.decompress(lz.compress(data))[0] == data
