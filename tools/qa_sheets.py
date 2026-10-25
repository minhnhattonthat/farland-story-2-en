"""qa_sheets.py: contact sheets for the visual-QA gate (qa_gate.py) from the phase-8 tours.

- pages: every <tour>/<run>/page_*.png (tools/lua/pageshot.lua) -> <out>/<name>/<run>.png (+ _2, _3 ... pages),
  full size, 3 x 3 per sheet;
- scenes: <scenes>/shots/*.png (tools/debug/regen.py) beside the same scene on the original ROM (--jp shots),
  4 pairs per sheet -> <out>/scenes/scenes_NN.png.

    python -X utf8 tools/qa_sheets.py --out work/qa/p8/sheets --pages tour=work/qa/p8/tour view=work/qa/p8/view
           --scenes work/qa/p8/scenes --jp work/qa/p8/scenes_jp
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

SHEET = os.path.join(SCRIPTS, "sheet.py")


def sheet(files, out, *extra):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-X", "utf8", SHEET, *map(str, files), "--out", str(out), *extra],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", nargs="*", default=[], metavar="NAME=DIR")
    ap.add_argument("--scenes")
    ap.add_argument("--jp")
    a = ap.parse_args()
    out = Path(a.out)
    for spec in a.pages:
        name, d = spec.split("=", 1)
        for run in sorted(p for p in Path(d).iterdir() if p.is_dir()):
            pages = sorted(run.glob("page_*.png"))
            if pages:
                sheet(pages, out / name / f"{run.name}.png", "--div", "1", "--cols", "3", "--max", "9")
    if a.scenes:
        shots = sorted(Path(a.scenes, "shots").glob("*.png"))
        shots = [s for s in shots if s.name != "sheet.png"]
        for i in range(0, len(shots), 4):
            extra = ["--compare", str(Path(a.jp, "shots"))] if a.jp else []
            sheet(shots[i:i + 4], out / "scenes" / f"scenes_{i // 4:02d}.png", "--div", "1", "--cols", "2",
                  "--max", "4", *extra)
    print(f"sheets in {out}")


if __name__ == "__main__":
    main()
