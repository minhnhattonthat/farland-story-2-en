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
STUB = 6  # a paragraph's last line shorter than this (characters) is a widow


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


def fill(body, n, px, last, w, fixed=False):
    """Lines of a paragraph body ({nl} = forced break); line i may hold `last` px when it ends a window page.
    fixed: a {clr} page, whose page-wait arrow sits on window line n whatever the page's length, so only line n
    gives way to it; else (scrolling narration) the final line does too."""
    def limit(i, final):
        return last if i % n == n - 1 or (final and not fixed) else px
    lines = []
    paras = body.split("{nl}")
    for k, para in enumerate(paras):
        start, cur = len(lines), ""
        for word in para.split(" "):
            cand = f"{cur} {word}" if cur else word
            if font.text_width(cand, w) <= limit(len(lines), False) or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        # no widow: pull words down from the line above while the last line is a stub (or one word) and still
        # fits, unless that leaves a single word on the line above
        lim = limit(len(lines), k == len(paras) - 1)
        while len(lines) > start and (len(cur) < STUB or " " not in cur) and " " in lines[-1]:
            head, word = lines[-1].rsplit(" ", 1)
            if font.text_width(f"{word} {cur}", w) > lim or (" " not in head and len(cur) >= STUB):
                break
            lines[-1], cur = head, f"{word} {cur}"
        lines.append(cur)
    lim = limit(len(lines) - 1, True)
    if font.text_width(lines[-1], w) > lim:  # the final line ends at the arrow too
        words = lines.pop().split(" ")
        k = len(words)
        while k > 1 and font.text_width(" ".join(words[:k]), w) > lim:
            k -= 1
        while k > 1 and len(" ".join(words[k:])) < STUB:  # no widow on the arrow line either
            k -= 1
        lines += [" ".join(words[:k]), " ".join(words[k:])]
    for i, line in enumerate(lines):
        if font.text_width(line, w) > limit(i, i == len(lines) - 1):
            raise ValueError(f"word too wide for the window: {line!r}")
    return lines


def sentences(body):
    """The body split after each sentence end (. ! ? and any closing quote) that a space follows."""
    out, i = [], 0
    for m in re.finditer(r"[.!?]+[\"')]*(?= )", body):
        out.append(body[i:m.end()])
        i = m.end() + 1
    return [x for x in out + [body[i:]] if x]


def page_chunks(body, n, px, last, w, fixed=False):
    """A paragraph too long for one window page -> page texts ({nl} between lines). Prefer page breaks at sentence
    ends when that takes no extra page; else keep the line fill, but a last page of one line takes the line above
    it too (3 + 1 -> 2 + 2, refilled)."""
    lines = fill(body, n, px, last, w, fixed)
    if len(lines) <= n:
        return ["{nl}".join(lines)]
    want = -(-len(lines) // n)
    if "{nl}" not in body:
        groups = []
        for s in sentences(body):
            if groups and len(fill(f"{groups[-1]} {s}", n, px, last, w, fixed)) <= n:
                groups[-1] = f"{groups[-1]} {s}"
            else:
                groups.append(s)
        filled = [fill(g, n, px, last, w, fixed) for g in groups]
        if len(groups) > 1 and sum(-(-len(f) // n) for f in filled) == want:
            return ["{nl}".join(f[i:i + n]) for f in filled for i in range(0, len(f), n)]
    chunks = [lines[i:i + n] for i in range(0, len(lines), n)]
    if len(chunks[-1]) == 1 and n > 1 and (fixed or font.text_width(chunks[-2][-2], w) <= last):
        tail = fill(f"{chunks[-2][-1]} {chunks[-1][0]}", n, px, last, w, fixed)
        if len(tail) <= n:
            chunks[-2:] = [chunks[-2][:-1], tail]
    return ["{nl}".join(c) for c in chunks]


def wrap_text(s, b, w=None):
    """Box string `s` wrapped to budget b = {px, lines, last}."""
    w = w or font.widths()
    n, px, last = b["lines"], b["px"], b.get("last", b["px"])
    out = []
    for prefix, body, suffix in pages(s):
        if not body or CODE.sub("", body.replace("{nl}", "")) != body.replace("{nl}", ""):
            out.append(prefix + body + suffix)  # empty or layout page
            continue
        chunks = page_chunks(body, n, px, last, w, "{clr}" in prefix)
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
    four = "{clr}" + " ".join(["word"] * 9) + ". " + " ".join(["more"] * 9) + "." + WAIT  # 4 lines
    out = wrap_text(four, b)
    assert out.count(WAIT) == 2 and out.split(WAIT)[0].endswith("word.") and wrap_text(out, b) == out, out
    assert all(p.count("{nl}") >= 1 for p in wrap_text("{clr}" + "x " * 85 + WAIT, b).split(WAIT)[:-1])  # 2 + 2
    assert " " in fill("aaa bbb ccc ddd eee fff ggg hhh iii jjj kkk lll mmm nnn ooo ppp qqq rrr sss " * 2 + "end.",
                       3, 143, 136, font.widths())[-1]  # no one-word last line
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
