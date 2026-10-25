# Compression

One LZ variant, decompressor `$C0:167D` (verified: `tools/lz.py` unpacks real blocks to exact power-of-two
sizes, e.g. `0x6321` -> 8192 bytes of 4bpp title tiles; `lz.py selftest` round-trips random data).

- Header: u16 LE = length of the packed stream after the header.
- Groups: one flag byte, then 8 items, flag bits LSB first (mask table `$C0:02E4` = 01 02 04 ... 80).
- Bit set: `count`, `offset` bytes; copy `count + 1` bytes from ring `[(write_pos + offset) & $FF]`, byte by byte.
- Bit clear: one literal byte. Every output byte also goes into the 256-byte ring (zero-filled at start, `$00:0187`).
- Stops when the read index reaches the length (can be mid-group).
- Our encoder (`lz.compress`) is greedy, not byte-identical to the original packer: the identity build copies
  original blocks unchanged and only recompresses edited ones. Verified on all 285 blocks
  (`tests/test_build.py`): each round-trips and packs no larger than the original, so an edited block whose
  data compresses as well fits in place.

## Blocks

`python -X utf8 tools/lzscan.py [--dump work/lz]` lists 285 blocks: 13 direct calls (immediate source) plus
the 3-byte pointer tables indexed by the other callers (`$C2:36CB`, `$C2:3548`, `$C2:3D91`, `$C2:456E`,
`$C2:4595`, `$C4:D2A9`, `$C4:D1E6`, `$C2:3D7C`, `$C2:42E8`). Table lengths are walked until an entry stops looking
like a block, so a few listed entries past a table's end may be false (e.g. `0x150000`, `0x150020`): guess.

Known contents: `0x6321` title-screen tiles incl. the menu labels (Bongo patched this block), `0x8065`,
`0x468C`, `0x9C3B` 8 KB tile sets loaded at boot / title. The rest (portraits, maps, battle sprites) is
classified in the graphics sweep (`graphics.md`).

Text is **not** compressed: all script and menu strings are raw 16-bit words (`text.md`).
