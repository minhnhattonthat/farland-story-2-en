"""Phase 5: VWF font data, English table, marker build. Every pointer of every string in the marker build leads
to that string's marker bytes (vm/p24 24-bit, imm 16-bit + bank immediate, p16 entry + the table's patched bank)."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import font  # noqa: E402
import marker  # noqa: E402
import wrap  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file() or not build.ASAR.is_file(), reason="ROM or asar absent")


def test_font_selftest():
    font.selftest()


def test_wrap_selftest():
    wrap.selftest()


def test_wrap_keeps_marker_layout():
    data, w = wrap.windows.load(), font.widths()
    for e in marker.fill(build.load_script()):
        assert wrap.wrap(e, data, w) == e["en"], e["id"]


def test_name_template_guard():
    en = font.english_table()
    entries = build.load_script()
    long_name = next(e for e in entries if e["id"].startswith("units.") and e["jp"])
    with pytest.raises(ValueError, match="name template"):
        build.name_templates([dict(e, en="A" * 17) if e is long_name else e for e in entries], en)


def test_marker_fits_box():
    w = font.widths()
    for e in marker.fill(build.load_script()):
        if e.get("box") and not e.get("notext"):
            for line in re.split(r"\{[^}]*\}", e["en"]):
                assert font.text_width(line, w) <= marker.BOX_DEFAULT["px"], e["id"]
            for before in e["en"].split("{wait}")[:-1]:  # the line before a page wait shares its row with the arrow
                last = re.split(r"\{[^}]*\}", before)[-1]
                assert font.text_width(last, w) <= marker.BOX_DEFAULT["last"], e["id"]


@needs_rom
def test_marker_build_pointers():
    rom = build.ROM.read_bytes()
    jp, en = build.Table.load(ROOT / "tbl" / "jp.tbl"), font.english_table()
    entries = build.name_templates(marker.fill(build.load_script()), en)
    out = build.english(rom, entries, {})
    assert len(out) == build.SIZE
    p16_bank = {}
    for base, n in build.p16_tables():
        banks = {out[s] for s in build.p16_bank_sites(rom, base, n)}
        assert len(banks) == 1, f"p16 table {base:06X}: mixed banks {banks}"
        p16_bank[base] = banks.pop()
    table_of = {base + 2 * i: base for base, n in build.p16_tables() for i in range(n)}
    for e in entries:
        want = (en.encode(e["en"]) if e["en"] else jp.encode(e["jp"])) + build.END
        for p in e["ptrs"]:
            kind, at = p.split(":")
            if kind in ("vm", "p24"):
                t = int.from_bytes(out[int(at, 16):int(at, 16) + 3], "little")
            elif kind == "p16":
                a = int(at, 16)
                t = p16_bank[table_of[a]] << 16 | int.from_bytes(out[a:a + 2], "little")
            else:
                lo, bank = (int(x, 16) for x in at.split("/"))
                t = out[bank] << 16 | int.from_bytes(out[lo:lo + 2], "little")
            t &= 0x3FFFFF
            assert out[t:t + len(want)] == want, f"{e['id']} via {p}"
