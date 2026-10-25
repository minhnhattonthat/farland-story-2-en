"""lint.py: the whole-script text lint (the build gate, run by tools/check.py through tests/test_lint.py).

Every entry with `en` gets the batch checks (tools/batches.py check_entry: font, pages, control codes, pixel
width per line against data/windows.json, glossary, honorifics), plus: no Japanese left in `en`, every entry with
Japanese text has `en` unless flagged `unused`/`notext`, and no box paragraph ends on a stub line (under 6 characters). Lines over a budget queued for engine work (`engine` in
data/windows.json) count as errors too: phase 7 is done when there are none.

    python -X utf8 tools/lint.py          # errors, then a count; exit 1 on any
"""
import contextlib
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches
import build
import font
import windows
import wrap

JP = re.compile(r"[぀-ヿ一-鿿]")
CODE = batches.CODE
STUB = 6


def en_text(e):
    """The translator-form text of an entry's `en` (what batches.check_entry takes)."""
    if batches.form(e) != "dlg":
        return e["en"]
    tp = batches.text_pages(e["en"])
    if tp is None:
        return None
    return batches.SEP.join(t for _, t in tp)


def lint_entry(e, gl, data, w, allowed):
    if not e["en"]:
        if not e.get("unused") and not e.get("notext") and CODE.sub("", e["jp"]).strip("　 "):
            return ["Japanese text with no `en` (flag it unused/notext if intended)"]
        return []
    errs = []
    if JP.search(e["en"]):
        errs.append("Japanese characters in `en`")
    text = en_text(e)
    if text is None:
        return errs + ["control codes inside an English dialogue page"]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):  # check_entry prints LONG lines for engine-queued fields
        errs += batches.check_entry(e, text, gl, data, w, allowed)
    errs += [line.split(": ", 1)[1] for line in out.getvalue().splitlines() if line.startswith("LONG ")]
    if e.get("box") and not errs:
        b = windows.budget(e, data)
        for _, body, _ in wrap.pages(e["en"]):
            if not body or CODE.search(body.replace("{nl}", "")):
                continue
            paras = body.split("{nl}")
            lines = wrap.fill(body, b["lines"], b["px"], b.get("last", b["px"]), w)
            if len(lines) > len(paras) and len(lines[-1]) < wrap.STUB:
                errs.append(f"stub last line {lines[-1]!r}")
    return errs


def lint(entries=None):
    """[(id, error)] over the whole script."""
    entries = entries if entries is not None else build.load_script()
    gl, data, w = batches.glossary(), windows.load(), font.widths()
    allowed = set(w) | {" "}
    return [(e["id"], x) for e in entries for x in lint_entry(e, gl, data, w, allowed)]


def main():
    errs = lint()
    for i, x in errs:
        print(f"{i}: {x}")
    print(f"lint: {len(errs)} errors")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
