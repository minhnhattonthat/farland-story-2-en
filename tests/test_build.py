"""Identity build (phase 3): unpack -> repack with no edits gives the dump byte for byte; keep green forever."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lz  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def unpacked():
    rom, table = build.ROM.read_bytes(), build.Table.load(ROOT / "tbl" / "jp.tbl")
    return rom, table, *build.unpack(rom, table)


@needs_rom
def test_identity(unpacked):
    rom, table, texts, blocks = unpacked
    assert len(texts) > 2000 and len(blocks) == 285
    assert build.repack(rom, table, texts, blocks) == rom


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
    rom, table, texts, blocks = unpacked
    text, n = texts[0x483D9]
    blocks = {0x6321: (blocks[0x6321][0], bytes(8192))}
    out = build.repack(rom, table, {0x483D9: (text.replace("アーク", "アアア", 1), n)}, blocks)
    assert table.decode(out, 0x483D9)[0].startswith("{full}アアアが")
    assert lz.decompress(out, 0x6321)[0] == bytes(8192)
    with pytest.raises(ValueError):
        build.repack(rom, table, {0x483D9: (text + "あ", n)}, {})
