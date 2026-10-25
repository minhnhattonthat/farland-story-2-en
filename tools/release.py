"""release.py: build -> tests -> smoke -> jp_left -> visual-QA gate -> checksum -> BPS (re-applied, compared) -> zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure. Writes release/FarlandStory2_EN_v<version>.{bps,zip} + README.txt (local, gitignored)
and keeps the playable patched image in build/farland2_en_v<version>.sfc. Refuses to overwrite an existing
version's files without --force. The QA tour is tools/qa_tour.py (about 25 minutes); this script refuses a build
whose sha1 differs from the one that tour shot (work/qa/p8/rom.sha1). The debug tool is Lua only
(tools/debug/warp.lua), so no debug code is ever in the ROM. Never publishes anything.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
BUILT = ROOT / "build" / "farland2_en.sfc"
QA = ROOT / "work" / "qa" / "p8"
NAME = "FarlandStory2_EN"
PY = [sys.executable, "-X", "utf8"]


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    if subprocess.run([*PY, *map(str, cmd)], cwd=ROOT).returncode:
        sys.exit(f"release: failed: {cmd[0]}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def slots(path):
    """Every English string's span in the build ("SLOT TARGET END", from build.py's write log), for jp_left."""
    english = {e["id"] for f in (ROOT / "script").glob("*.json")
               for e in json.loads(f.read_text(encoding="utf-8")) if e["en"]}
    rows = [f"{int(off, 16):06X} {int(off, 16):06X} {int(off, 16) + len(new) // 2:06X}\n"
            for off, _, new, *by in (line.split() for line in BUILT.with_suffix(".writes.txt").read_text().splitlines())
            if by and by[0] in english and len(by) == 1]
    path.write_text("".join(rows))
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()
    out = ROOT / "release"
    patch, zpath = out / f"{NAME}_v{a.version}.bps", out / f"{NAME}_v{a.version}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"release: {patch.name} or {zpath.name} exists; pass --force to overwrite")

    run(ROOT / "tools" / "build.py")
    run(ROOT / "tools" / "check.py")
    run(Path(SCRIPTS) / "emu.py", BUILT, "--out", ROOT / "work" / "qa" / "smoke", "--route",
        ROOT / "tools" / "routes" / "boot.txt", "--smoke")
    work = ROOT / "work" / "release"
    work.mkdir(parents=True, exist_ok=True)
    print(f"jp_left: {slots(work / 'slots.txt')} English strings")
    run(Path(SCRIPTS) / "jp_left.py", BUILT, "--tbl", ROOT / "tbl" / "jp.tbl", "--slots", work / "slots.txt")
    built = BUILT.read_bytes()
    shot = (QA / "rom.sha1").read_text().strip() if (QA / "rom.sha1").exists() else "none"
    if shot != hashlib.sha1(built).hexdigest():
        sys.exit(f"release: the QA tour shot build {shot}, not this one: run tools/qa_tour.py, then the visual-QA gate")
    run(Path(SCRIPTS) / "qa_gate.py", "check", QA / "manifest.tsv")

    final = ROOT / "build" / f"farland2_en_v{a.version}.sfc"
    run(ROOT / "tools" / "bps.py", "snes-checksum", BUILT, "--out", final)
    out.mkdir(exist_ok=True)
    run(ROOT / "tools" / "bps.py", "make", ROM, final, patch)
    check = work / "reapplied.sfc"
    run(ROOT / "tools" / "bps.py", "apply", ROM, patch, check)
    if check.read_bytes() != final.read_bytes():
        sys.exit("release: the re-applied patch differs from the build")
    check.unlink()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = (readme.replace("{VERSION}", a.version).replace("{BASE}", hashes(ROM.read_bytes()))
              .replace("{PATCHED}", hashes(final.read_bytes())))
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release: {zpath.relative_to(ROOT)} (patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}); "
          f"playable image {final.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
