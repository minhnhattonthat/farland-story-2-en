"""wrap.py: fit English box text to its window by pixel width (tools/font.py widths, data/windows.json budgets).

A box string is a run of pages: `<prefix codes><text>{wait}`. Translators write each page's text as one paragraph
(forced breaks: `{nl}`); `wrap()` breaks it into lines of at most `px` pixels (`last` px for the line before a
page wait: the arrow) and, when a page needs more lines than the window has, splits it into more pages with the
same prefix (`{clr}` pages) or `{wait}{nl}` (scrolling narration, no `{clr}`). Lines that already fit are kept,
so wrapping is idempotent. Pages whose text holds other codes ({half}, {pos}: credits, stage cards) are layout
and stay as written. build.py wraps every box entry at encode time.

    python -X utf8 tools/wrap.py "English text {wait}" [--box upper]   # dry run: lines with their widths
    python -X utf8 tools/wrap.py --id ch01.0493B7                      # an entry's wrapped `en`
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font
import windows

CODE = re.compile(r"(\{[^}]*\})")
WAIT = "{wait}"


def pages(s):
    """[(prefix codes, body, suffix)] split after each {wait}; body keeps its inner codes."""
    out = []
    for seg in re.split(r"(?<=\{wait\})", s):
        if not seg:
            continue
        toks = [t for t in CODE.split(seg) if t]
        i = 0
        while i < len(toks) and CODE.fullmatch(toks[i]):
            i += 1
        rest = "".join(toks[i:])
        suffix = WAIT if rest.endswith(WAIT) else ""
        out.append(("".join(toks[:i]), rest[:len(rest) - len(suffix)], suffix))
    return out


def fill(body, n, px, last, w):
    """Lines of a paragraph body ({nl} = forced break); line i may hold `last` px when it ends a window page."""
    lines = []
    for para in body.split("{nl}"):
        cur = ""
        for word in para.split(" "):
            cand = f"{cur} {word}" if cur else word
            lim = last if len(lines) % n == n - 1 else px
            if font.text_width(cand, w) <= lim or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    if font.text_width(lines[-1], w) > last:  # the page's final line ends at the arrow too
        words = lines.pop().split(" ")
        k = len(words)
        while k > 1 and font.text_width(" ".join(words[:k]), w) > last:
            k -= 1
        lines += [" ".join(words[:k]), " ".join(words[k:])]
    for i, line in enumerate(lines):
        if font.text_width(line, w) > (last if i % n == n - 1 or i == len(lines) - 1 else px):
            raise ValueError(f"word too wide for the window: {line!r}")
    return lines


def wrap_text(s, b, w=None):
    """Box string `s` wrapped to budget b = {px, lines, last}."""
    w = w or font.widths()
    n, px, last = b["lines"], b["px"], b.get("last", b["px"])
    out = []
    for prefix, body, suffix in pages(s):
        if not body or CODE.sub("", body.replace("{nl}", "")) != body.replace("{nl}", ""):
            out.append(prefix + body + suffix)  # empty or layout page
            continue
        lines = fill(body, n, px, last, w)
        chunks = ["{nl}".join(lines[i:i + n]) for i in range(0, len(lines), n)]
        again = prefix if "{clr}" in prefix else "{nl}"
        out.append(prefix + (WAIT + again).join(chunks) + (suffix or (WAIT if len(chunks) > 1 else "")))
    return "".join(out)


def wrap(e, data=None, w=None):
    """An entry's `en` as it goes into the ROM: box text wrapped, anything else unchanged."""
    if not e.get("en") or not e.get("box"):
        return e.get("en", "")
    return wrap_text(e["en"], windows.budget(e, data or windows.load()), w)


def selftest():
    b = {"px": 143, "lines": 3, "last": 136}
    s = "{clr}{pos:00000000}{full}" + " ".join(["word"] * 40) + WAIT
    out = wrap_text(s, b)
    assert out.count(WAIT) == out.count("{clr}") == 3, out
    assert wrap_text(out, b) == out  # idempotent
    assert wrap_text("{full}" + "x " * 60 + WAIT, b).count("{wait}{nl}") == 1  # scrolling narration
    layout = "{clr}{pos:00000000}{half}A{nl}{pos:02000000}B" + WAIT
    assert wrap_text(layout, b) == layout
    try:
        wrap_text("{clr}" + "W" * 30 + WAIT, b)
        raise AssertionError("too-wide word passed")
    except ValueError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--box", default="upper")
    ap.add_argument("--id")
    a = ap.parse_args()
    data, w = windows.load(), font.widths()
    if a.id:
        import build
        e = next(e for e in build.load_script() if e["id"] == a.id)
        print(wrap(e, data, w))
        return
    out = wrap_text(a.text, data["box"][a.box], w)
    for page in out.split(WAIT)[:-1] + [p for p in out.split(WAIT)[-1:] if CODE.sub("", p)]:
        for line in re.split(r"\{nl\}", page):
            text = CODE.sub("", line)
            if text:
                print(f"{font.text_width(text, w):4d}px  {text}")
        print("  ----")


if __name__ == "__main__":
    main()
