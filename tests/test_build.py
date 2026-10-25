"""Identity build (phase 3) and extraction (phase 4): unpack -> repack gives the dump byte for byte; every script
string re-encodes to its original bytes; the text ranges are fully covered. Keep green forever."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import extract  # noqa: E402
import lz  # noqa: E402
import textscan  # noqa: E402
import vm  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def unpacked():
    rom, table = build.ROM.read_bytes(), build.Table.load(ROOT / "tbl" / "jp.tbl")
    return rom, table, *build.unpack(rom, table)


@needs_rom
def test_identity(unpacked):
    rom, table, entries, blocks = unpacked
    assert len(entries) > 1800 and len(blocks) == 285
    assert build.repack(rom, table, entries, blocks) == rom


@needs_rom
def test_script_files_roundtrip(unpacked):
    """Every script/*.json string encodes back to the ROM bytes it came from, and the files hold exactly the
    strings a fresh extraction finds (same ids, same jp)."""
    rom, table, entries, _ = unpacked
    files = build.load_script()
    for e in files:
        a = int(e["addr"], 16)
        assert table.encode(e["jp"]) + build.END == rom[a:a + e["len"]], e["id"]
    assert {e["id"]: e["jp"] for e in files} == {e["id"]: e["jp"] for e in entries}


@needs_rom
def test_text_ranges_fully_covered(unpacked):
    """Every run that scans as text inside the text ranges belongs to an extracted string (or is listed non-text)."""
    rom, _, entries, _ = unpacked
    covered = bytearray(len(rom))
    for e in entries:
        a = int(e["addr"], 16)
        covered[a:a + e["len"]] = b"\x01" * e["len"]
    gaps = [f"{s:06X}" for s, e in textscan.runs(rom, 3, 2)
            if extract.in_text_ranges(s) and s not in extract.NOT_TEXT and not all(covered[s:e])]
    assert not gaps


@needs_rom
def test_strings_do_not_overlap(unpacked):
    spans = sorted((int(e["addr"], 16), e["len"]) for e in unpacked[2])
    assert all(a + n <= b for (a, n), (b, _) in zip(spans, spans[1:]))


@needs_rom
def test_vm_walk(unpacked):
    """The bytecode walker decodes every reachable op (a wrong argument length raises) from every chapter."""
    rom = unpacked[0]
    code = vm.walk(rom)
    chapters = [vm.off(int.from_bytes(rom[0xC9F0 + 3 * c:0xC9F3 + 3 * c], "little")) for c in range(vm.CHAPTERS)]
    starts = vm.entries(rom)
    assert all(any(c <= s < c + 0x40 for s in starts.values()) for c in chapters)
    assert len(vm.text_refs(rom, code)) > 1300


@needs_rom
def test_every_lz_block_recompresses_in_place(unpacked):
    """Our packer round-trips every block and never needs more room than the original (~40 s)."""
    rom, _, _, blocks = unpacked
    for src, (size, data) in blocks.items():
        packed = lz.compress(data)
        assert lz.decompress(packed)[0] == data, hex(src)
        assert len(packed) <= size, hex(src)


@needs_rom
def test_edits_reach_the_output(unpacked):
    rom, table, entries, blocks = unpacked
    e = dict(next(e for e in entries if e["addr"] == "0483D9"))
    e["en"] = e["jp"].replace("アーク", "アアア", 1)
    blocks = {0x6321: (blocks[0x6321][0], bytes(8192))}
    out = build.repack(rom, table, [e], blocks)
    assert table.decode(out, 0x483D9)[0].startswith("{full}アアアが")
    assert lz.decompress(out, 0x6321)[0] == bytes(8192)
    with pytest.raises(ValueError):
        build.repack(rom, table, [{**e, "en": e["jp"] + "あ"}], {})


def test_script_files_are_valid_json():
    for p in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(p.read_text(encoding="utf-8")):
            assert {"id", "addr", "len", "ptrs", "jp", "en"} <= e.keys(), (p.name, e.get("id"))
