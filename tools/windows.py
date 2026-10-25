"""windows.py: text-window sizes seen in a tour (tools/lua/textlog.lua logs) -> data/windows.json `entries`.

Each string the engine started is matched to its script entry (pointer = the entry's address; strings drawn
from a RAM buffer are matched to the entries whose text the buffer contains). Per entry: window id,
width in 8-px cells, lines. The `box` part of data/windows.json (measured pixel budgets per box type) is kept.
Run on a tour of a build whose strings sit at their original addresses (no English: tools/build.py without
`--marker`, as tour_jp.sfc).

    python -X utf8 tools/windows.py work/qa/tour5 work/qa/tour6 [--write]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = ROOT / "data" / "windows.json"
STR = re.compile(r"str f(\d+) ([0-9A-F]{6}) win=([0-9A-F]{2}) w=(\d+) h=(\d+) mode=([0-9A-F]{2})(?: buf=([0-9A-F]+))?")
CTRL = re.compile(r"\{[^}]*\}")


def strip(s):
    return CTRL.sub("", s).replace("　", "")


def scan(tours):
    """{entry id: {win, cells, lines, via}} from every log.txt under the tour dir."""
    entries = build.load_script()
    by_addr = {int(e["addr"], 16): e["id"] for e in entries}
    texts = [(e["id"], strip(e["jp"])) for e in entries if not e.get("notext") and len(strip(e["jp"])) >= 2]
    jp = build.Table.load(ROOT / "tbl" / "jp.tbl")
    seen = {}
    for log in sorted(p for t in tours for p in Path(t).glob("*/log.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if m := STR.match(line):
                p = int(m[2], 16)
                info = {"win": m[3], "cells": int(m[4]), "lines": int(m[5])}
                if m[7]:  # RAM buffer: the entries whose text it contains
                    buf = strip(jp.decode(bytes.fromhex(m[7]))[0])
                    ids = [i for i, t in texts if t in buf]
                    info["via"] = f"{p:06X}"
                else:
                    ids = [by_addr[p & 0x3FFFFF]] if p & 0x3FFFFF in by_addr else []
                for i in ids:
                    old = seen.get(i)
                    if not old or info["cells"] < old["cells"]:  # one string, several windows: the smallest
                        seen[i] = info
    return seen


def load():
    return json.loads(WINDOWS.read_text(encoding="utf-8")) if WINDOWS.exists() else {}


def budget(e, data):
    """{px, lines[, last]} for an entry: its box type, its file's field, or (system) its seen window less the
    start cell of its first {pos}. None = not measured yet."""
    if e.get("box"):
        return data["box"][e["box"].split("/")[0]]
    if e["id"] in data.get("override", {}):  # fields that share their row with numbers or other strings
        return data["override"][e["id"]]
    f = data.get("fields", {}).get(e["id"].split(".")[0])
    if f and "px" in f:
        return f
    w = None
    for base, t in data.get("tables", {}).items():
        if any(p.startswith("p16:") and 0 <= int(p[4:], 16) - int(base, 16) < 2 * t["entries"] for p in e["ptrs"]):
            w = t
    w = w or data.get("entries", {}).get(e["id"]) or data.get("static", {}).get(e["id"])
    if not w:
        return None
    m = re.search(r"\{pos:([0-9A-F]{4})", e["jp"])
    col = int(m[1][2:] + m[1][:2], 16) if m else 0
    return {"px": (w["cells"] - col) * 8 - 1, "lines": w["lines"]}


def report():
    data = load()
    todo = [e for e in build.load_script() if not e.get("notext") and not e.get("unused") and not budget(e, data)]
    guess = [i for i in data.get("static", {}) if not i.startswith("_")]
    print(f"{len(todo)} strings with text have no budget:", " ".join(e["id"] for e in todo[:40]),
          "..." if len(todo) > 40 else "")
    print(f"{len(guess)} budgets are static guesses (data/windows.json `static`); measure when a scene shows them")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tour", nargs="*")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if not a.tour:
        return report()
    seen = scan(a.tour)
    entries = build.load_script()
    todo = [e["id"] for e in entries if not e.get("notext") and not e.get("unused") and e["id"] not in seen]
    sizes = {}
    for v in seen.values():
        k = (v["cells"], v["lines"], "via" in v)
        sizes[k] = sizes.get(k, 0) + 1
    print(f"{len(seen)} entries seen, {len(todo)} with text not seen")
    for (c, l, via), n in sorted(sizes.items()):
        print(f"  {c:2d} cells x {l} lines{' (buffer)' if via else ''}: {n}")
    if a.write:
        data = json.loads(WINDOWS.read_text(encoding="utf-8")) if WINDOWS.exists() else {}
        data["entries"] = dict(sorted(seen.items()))
        WINDOWS.parent.mkdir(exist_ok=True)
        WINDOWS.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {WINDOWS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
