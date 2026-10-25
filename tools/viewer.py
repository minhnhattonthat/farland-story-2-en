"""viewer.py: show script strings no warp reaches (mid- and post-battle dialogue) in a real dialogue box.

Each run loads HOST's savestate (a chapter warp, saved by tools/debug/regen.py), and tools/lua/viewer.lua swaps
every string that chapter's story starts for the next one of the list; tools/lua/pageshot.lua shoots each page.
A run that runs out of host strings leaves the rest of its chunk for the next round.

    python -X utf8 tools/viewer.py LIST --state work/qa/p8/tour/states/ch17.mss --host ch17 --out work/qa/p8/view
           [--rom build/farland2_en.sfc] [--chunk 12] [--jobs 4]

LIST: "<id> <hex address>" lines (tools/coverage.py --missing). Out: <out>/v<NNN>/ (page_*.png, log.txt with
"view <id> f<frame>" lines), <out>/viewed.txt (id, run dir, frame of its first page).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

EMU = os.path.join(SCRIPTS, "emu.py")
LUA = ROOT / "tools" / "lua"


def run(rom, state, host, lst, first, last, out):
    shutil.rmtree(out, ignore_errors=True)
    cmd = [sys.executable, "-X", "utf8", EMU, str(rom), "--out", str(out), "--state-in", str(state),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{host}'",
           "--var", "HOLD=60000", "--var", "CLICK=0", "--var", "FAST=1", "--var", "PAGE_DELAY=40",
           "--script", str(LUA / "pageshot.lua"), "--script", str(LUA / "viewer.lua"),
           "--var", f"VIEW=[[{Path(lst).resolve().as_posix()}]]", "--var", f"FIRST={first}", "--var", f"LAST={last}",
           "--frames", "60600", "--timeout", "1200"]
    subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    return [(m[1], int(m[2])) for m in re.finditer(r"^view (\S+) f(\d+)", log, re.M)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("list")
    ap.add_argument("--state", required=True)
    ap.add_argument("--host", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rom", default=str(ROOT / "build" / "farland2_en.sfc"))
    ap.add_argument("--chunk", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    todo = [l.split()[0] for l in Path(a.list).read_text().splitlines() if l.strip()]
    lines = {l.split()[0]: l for l in Path(a.list).read_text().splitlines() if l.strip()}
    viewed, n = {}, 0
    while todo:
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        jobs = []
        for c in chunks:
            lst = out / f"v{n:03d}.txt"
            lst.write_text("".join(lines[i] + "\n" for i in c))
            jobs.append((lst, len(c), out / f"v{n:03d}"))
            n += 1
        with ThreadPoolExecutor(a.jobs) as ex:
            res = list(ex.map(lambda j: (j[2], run(a.rom, a.state, a.host, j[0], 1, j[1], j[2])), jobs))
        for d, got in res:
            for i, f in got:
                viewed.setdefault(i, (d.name, f))
        left = [i for i in todo if i not in viewed]
        if len(left) == len(todo):
            print(f"no progress; {len(left)} strings not viewed (see {out}/v*/log.txt)")
            break
        todo = left
        print(f"round done: {len(viewed)} viewed, {len(todo)} left")
    (out / "viewed.txt").write_text("".join(f"{i}\t{d}\t{f}\n" for i, (d, f) in sorted(viewed.items())))
    sys.exit(1 if todo else 0)


if __name__ == "__main__":
    main()
