"""regen.py: warp to every scene in tools/debug/scenes.lua from a cold boot, keep a shot and a savestate of each.

    python -X utf8 tools/debug/regen.py [SCENE ...] [--rom ROM] [--jobs 4] [--cold]

Out: work/qa/warp/<scene>/ (emu.py run), work/qa/warp/shots/<scene>.png + contact sheets, work/states/<scene>.mss.
`map` is warped first; the other battle-map scenes start from its state (pass --cold to boot each one cold).
Exit 1 if any scene was not reached. Regenerate after any code, font or graphics change: states keep old VRAM.
"""
import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

EMU = os.path.join(SCRIPTS, "emu.py")
WARP = ROOT / "tools" / "debug" / "warp.lua"
OUT = ROOT / "work" / "qa" / "warp"
STATES = ROOT / "work" / "states"


EXTRA = {"scripts": [], "hold": 0}  # --script / --hold (text tours)


def emu(rom, out, scene, frames, state_in=None, state_out=None):
    frames += EXTRA["hold"]
    cmd = [sys.executable, "-X", "utf8", EMU, str(rom), "--out", str(out), "--script", str(WARP),
           "--var", f"SCENE='{scene}'", "--frames", str(frames), "--timeout", str(frames // 60 + 120)]
    for s in EXTRA["scripts"]:
        cmd += ["--script", str(s)]
    if EXTRA["hold"]:
        cmd += ["--var", f"HOLD={EXTRA['hold']}"]
    if EXTRA.get("shot_every"):
        cmd += ["--shot-every", str(EXTRA["shot_every"])]
    for v in EXTRA.get("vars", []):
        cmd += ["--var", v]
    if state_out:
        cmd += ["--var", f"DONE_STATE=[[{Path(state_out).as_posix()}]]"]
    if state_in:
        cmd += ["--state-in", str(state_in)]
    subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    log = out / "log.txt"
    return log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""


def list_scenes(rom):
    log = emu(rom, OUT / "_list", "__list", 10)
    scenes = sorted(l.split()[1:3] for l in log.splitlines() if l.startswith("scene "))
    if not scenes:
        sys.exit("warp.lua listed no scenes: see work/qa/warp/_list/")
    return dict(scenes)


def run(rom, scene, kind, cold):
    out = OUT / scene
    shutil.rmtree(out, ignore_errors=True)
    state_in = None if cold or kind != "map" or scene == "map" else STATES / "map.mss"
    frames = 8000 if state_in else 60000
    log = emu(rom, out, scene, frames, state_in, STATES / f"{scene}.mss")
    if "warp reached" not in log:  # a run now and then never leaves the title (no warp line at all): retry once
        shutil.rmtree(out, ignore_errors=True)
        log = emu(rom, out, scene, frames, state_in, STATES / f"{scene}.mss")
    ok = "warp reached" in log
    if ok:
        shutil.copy(out / f"{scene}.png", OUT / "shots" / f"{scene}.png")
    line = next((l for l in log.splitlines() if l.startswith("warp reached")), "NOT REACHED")
    return scene, ok, line


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--rom", default=ROOT / "rom" / "Farland Story 2 (Japan).sfc")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--cold", action="store_true", help="boot every scene cold (no map.mss shortcut)")
    ap.add_argument("--out", help="output dir instead of work/qa/warp (states go to <out>/states)")
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe for every run (repeatable)")
    ap.add_argument("--hold", type=int, default=0, help="keep clicking A this many frames after each scene")
    ap.add_argument("--shot-every", type=int, default=0, help="also shoot every N frames (emu.py)")
    ap.add_argument("--var", action="append", default=[], help="NAME=LUA global for every run (repeatable)")
    a = ap.parse_args()
    global OUT, STATES
    if a.out:
        OUT = Path(a.out).resolve()
        STATES = OUT / "states"
    EXTRA["scripts"] = [Path(s).resolve() for s in a.script]
    EXTRA["hold"] = a.hold
    EXTRA["shot_every"] = a.shot_every
    EXTRA["vars"] = a.var
    all_scenes = list_scenes(a.rom)
    names = a.scenes or sorted(all_scenes)
    bad = [n for n in names if n not in all_scenes]
    if bad:
        sys.exit(f"unknown scene(s): {' '.join(bad)}")
    (OUT / "shots").mkdir(parents=True, exist_ok=True)
    STATES.mkdir(parents=True, exist_ok=True)
    results = []
    need_map = not a.cold and any(all_scenes[n] == "map" and n != "map" for n in names)
    if need_map or "map" in names:  # the battle-map scenes start from map.mss
        results.append(run(a.rom, "map", "map", True))
        if not results[-1][1]:
            print("map not reached: battle-map scenes run cold")
            a.cold = True
    rest = [n for n in names if n != "map"]
    with ThreadPoolExecutor(a.jobs) as ex:
        results += list(ex.map(lambda n: run(a.rom, n, all_scenes[n], a.cold), rest))
    for scene, ok, line in sorted(results):
        print(f"{'ok ' if ok else 'BAD'} {scene:14} {line}")
    shots = sorted((OUT / "shots").glob("*.png"))
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", os.path.join(SCRIPTS, "sheet.py"), *map(str, shots),
                        "--out", str(OUT / "sheet.png")], cwd=ROOT, stdout=subprocess.DEVNULL)
    failed = [s for s, ok, _ in results if not ok]
    print(f"{len(results) - len(failed)}/{len(results)} scenes reached; shots in {OUT / 'shots'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
