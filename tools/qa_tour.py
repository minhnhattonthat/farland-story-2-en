"""qa_tour.py: the phase-8 QA tour of a build, start to finish, for the visual-QA gate.

1. every warp scene, one shot each (tools/debug/regen.py) -> <out>/scenes (+ states);
2. every chapter's story, one shot per page (tools/lua/pageshot.lua) -> <out>/tour;
3. the box strings no chapter start shows (tools/coverage.py) drawn by the string viewer (tools/viewer.py,
   host: chapter 0's story) -> <out>/view;
4. contact sheets (tools/qa_sheets.py, scenes paired with <out>/scenes_jp) -> <out>/sheets, and
   `qa_gate.py init <out>/manifest.tsv <out>/sheets` (unchanged sheets keep their verdicts).

    python -X utf8 tools/qa_tour.py [--rom build/farland2_en.sfc] [--out work/qa/p8] [--jp] [--skip scenes,tour,view]

--jp also shoots the scenes on the original ROM (once; <out>/scenes_jp). About 25 minutes with 4 jobs.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
PAGES = ["--hold", "40000", "--script", str(ROOT / "tools/lua/pageshot.lua"), "--script",
         str(ROOT / "tools/lua/textlog.lua"), "--var", "CLICK=0", "--var", "FAST=1", "--var", "PAGE_DELAY=40"]


def step(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    r = subprocess.run([*PY, *map(str, cmd)], cwd=ROOT)
    if r.returncode:
        sys.exit(f"failed ({r.returncode}): {cmd[0]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default=str(ROOT / "build" / "farland2_en.sfc"))
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "p8"))
    ap.add_argument("--jp", action="store_true")
    ap.add_argument("--skip", default="")
    a = ap.parse_args()
    out, skip = Path(a.out), set(a.skip.split(","))
    regen = ROOT / "tools/debug/regen.py"
    if a.jp:
        step(regen, "--out", out / "scenes_jp")
    if "scenes" not in skip:
        shutil.rmtree(out / "scenes", ignore_errors=True)
        step(regen, "--rom", a.rom, "--out", out / "scenes")
    if "tour" not in skip:
        shutil.rmtree(out / "tour", ignore_errors=True)
        step(regen, *[f"ch{i:02d}" for i in range(39)], "--rom", a.rom, "--out", out / "tour", *PAGES)
    if "view" not in skip:
        shutil.rmtree(out / "view", ignore_errors=True)
        step(ROOT / "tools/coverage.py", out / "tour", "--rom", a.rom, "--missing", out / "missing.txt")
        step(ROOT / "tools/viewer.py", out / "missing.txt", "--state", out / "tour/states/ch00.mss", "--host", "ch00",
             "--out", out / "view", "--rom", a.rom, "--chunk", "40", "--jobs", "5")
    shutil.rmtree(out / "sheets", ignore_errors=True)
    step(ROOT / "tools/qa_sheets.py", "--out", out / "sheets", "--pages", f"tour={out / 'tour'}",
         f"view={out / 'view'}", "--scenes", out / "scenes", "--jp", out / "scenes_jp")
    manifest = out / "manifest.tsv"
    if manifest.exists():  # sheets this tour no longer makes (fewer pages) leave the gate
        rows = manifest.read_text(encoding="utf-8").splitlines()
        manifest.write_text("".join(r + "\n" for r in rows if (ROOT / r.split("\t")[1]).exists()
                                    or Path(r.split("\t")[1]).exists()), encoding="utf-8")
    step(os.path.join(SCRIPTS, "qa_gate.py"), "init", manifest, out / "sheets", "--glob", "*.png")
    if not skip - {""}:  # tools/release.py refuses a build this full tour didn't shoot
        (out / "rom.sha1").write_text(hashlib.sha1(Path(a.rom).read_bytes()).hexdigest() + "\n")


if __name__ == "__main__":
    main()
