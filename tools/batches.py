"""batches.py: translation batches for agents (docs/translator-brief.md), their check, merge and review pairs.

    python -X utf8 tools/batches.py split script/ch0*.json [--chars 3500]   # -> work/tl/bNNN.tsv + .terms.txt
    python -X utf8 tools/batches.py check b001 [b002 ..]                    # exit 1 on any error
    python -X utf8 tools/batches.py merge b001 [..]                         # checked output -> script/*.json `en`
    python -X utf8 tools/batches.py pairs b001                              # -> work/tl/b001.pairs.txt (reviewer)

Input TSV: `id<TAB>box<TAB>form<TAB>limit<TAB>jp`. form `dlg` = box text: the pages' text without codes, joined by
` || `; the English gives the same number of pages and tools/wrap.py breaks lines (and adds pages) by pixel width.
form `layout` = anything else: the Japanese with its control codes, which the English keeps in the same order
(`{nl}` may differ), each line within `limit` px and at most that many lines. Output: `work/tl/<batch>.out.tsv`,
`id<TAB>English`. Entries with no text, `unused` or `notext` entries, and ids already in a batch are skipped.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build
import font
import windows
import wrap

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work" / "tl"
GLOSSARY = ROOT / "glossary.md"
CODE = re.compile(r"\{[^}]*\}")
KATA = "ァ-ヺー"
SEP = " || "
HONORIFICS = {"さま": "-sama", "様": "-sama", "さん": "-san", "くん": "-kun", "ちゃん": "-chan", "どの": "-dono", "殿": "-dono"}


def text_pages(jp):
    """Indices and texts of the pages of a box string that carry text, or None if a page is layout."""
    out = []
    for i, (_, body, _) in enumerate(wrap.pages(jp)):
        flat = body.replace("{nl}", "")
        if CODE.search(flat):
            return None
        if flat.strip("　 "):
            out.append((i, flat))
    return out


def form(e):
    return "dlg" if e.get("box") and text_pages(e["jp"]) else "layout"


def glossary():
    """[(section, jp, en)] from the glossary tables."""
    rows, section = [], ""
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-"):
            rows.append((section, cells[0], cells[1], line))
    return rows


def term_in(jp_term, text):
    """Whole-run match for katakana terms (ミン must not match inside タイミング), substring otherwise."""
    if re.fullmatch(f"[{KATA}・]+", jp_term):
        return re.search(f"(?<![{KATA}]){re.escape(jp_term)}(?![{KATA}])", text) is not None
    return jp_term in text


def entries_by_id():
    return {e["id"]: e for e in build.load_script()}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def split(files, chars):
    TL.mkdir(parents=True, exist_ok=True)
    done = {r[0] for p in TL.glob("b[0-9][0-9][0-9].tsv") for r in read_tsv(p)}
    nums = [int(p.stem[1:]) for p in TL.glob("b[0-9][0-9][0-9].tsv")]
    num = max(nums, default=0) + 1
    data, gl = windows.load(), glossary()
    batches, cur, size, last_file = [], [], 0, None
    for f in files:
        for e in json.loads(Path(f).read_text(encoding="utf-8")):
            if e.get("notext") or e.get("unused") or e["en"] or e["id"] in done:
                continue
            if not CODE.sub("", e["jp"]).strip("　 "):
                continue
            n = len(CODE.sub("", e["jp"]))
            if cur and (size + n > chars or (Path(f).name != last_file and size > chars * 0.6)):
                batches.append(cur)
                cur, size = [], 0
            cur.append(e)
            size += n
            last_file = Path(f).name
    if cur:
        batches.append(cur)
    for es in batches:
        name = f"b{num:03d}"
        num += 1
        rows = []
        for e in es:
            fm = form(e)
            if fm == "dlg":
                jp, limit = SEP.join(t for _, t in text_pages(e["jp"])), f"box {e['box']} (auto-wrap)"
            else:
                b = windows.budget(e, data)
                jp, limit = e["jp"], f"{b['px']}px x{b['lines']}" if b else "?"
            rows.append("\t".join([e["id"], e.get("box") or "-", fm, limit, jp]))
        (TL / f"{name}.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        terms = [line for _, j, _, line in gl if any(term_in(j, e["jp"]) for e in es)]
        (TL / f"{name}.terms.txt").write_text("| JP | EN | max | notes | Avoid |\n" + "\n".join(terms) + "\n",
                                              encoding="utf-8", newline="\n")
        print(f"{name}: {len(es)} entries, {sum(len(CODE.sub('', e['jp'])) for e in es)} chars, "
              f"{es[0]['id']} .. {es[-1]['id']}")


def compose(e, en_text):
    """The `en` field for an entry from the translator's text."""
    if form(e) == "layout":
        return en_text
    ps = wrap.pages(e["jp"])
    texts = dict(zip((i for i, _ in text_pages(e["jp"])), en_text.split(SEP)))
    return "".join(p + texts[i] + s if i in texts else p + b + s for i, (p, b, s) in enumerate(ps))


def check_entry(e, en_text, gl, data, w, allowed):
    errs = []
    bad = sorted({c for c in CODE.sub("", en_text.replace(SEP, "")) if c not in allowed or c == font.ZWSP})
    if bad or "\\u" in en_text:
        errs.append(f"characters not in the font: {''.join(bad) or '\\u'}")
    fm = form(e)
    if fm == "dlg":
        n_jp, n_en = len(text_pages(e["jp"])), len(en_text.split(SEP))
        if n_jp != n_en:
            errs.append(f"{n_en} pages, the Japanese has {n_jp} (separate pages with ' || ')")
        elif CODE.search(en_text.replace("{nl}", "")):
            errs.append("control codes in dialogue text (only {nl} allowed)")
        else:
            try:
                wrap.wrap(dict(e, en=compose(e, en_text)), data, w)
            except ValueError as x:
                errs.append(str(x))
    else:
        strip_nl = lambda s: [c for c in CODE.findall(s) if c != "{nl}"]  # noqa: E731
        if strip_nl(e["jp"]) != strip_nl(en_text):
            errs.append(f"control codes differ: want {''.join(strip_nl(e['jp']))}")
        b = windows.budget(e, data)
        if b:
            lines = en_text.split("{nl}")
            if len(lines) > b["lines"]:
                errs.append(f"{len(lines)} lines, window has {b['lines']}")
            for line in (s for ln in lines for s in re.split(r"\{pos:[^}]*\}", ln)):  # {pos} starts a new run
                px = font.text_width(CODE.sub("", line), w) if not bad else 0
                if px > b["px"]:
                    msg = f"line {px}px > {b['px']}px: {CODE.sub('', line)!r}"
                    if b.get("engine"):  # wider window queued: flag, don't cut (D4)
                        print(f"LONG {e['id']}: {msg} ({b['engine'][:8]})")
                    else:
                        errs.append(msg)
            if b.get("max_chars") and len(CODE.sub("", en_text)) > b["max_chars"]:
                errs.append(f"{len(CODE.sub('', en_text))} characters, at most {b['max_chars']}")
    names = {j: en for sec, j, en, _ in gl if sec == "Characters"}
    rest = e["jp"]
    for sec, j, en, _ in sorted(gl, key=lambda r: -len(r[1])):  # longest first: まほうこうげきりょく before こうげきりょく
        if not term_in(j, rest):
            continue
        rest = rest.replace(j, "■")
        forms = en.split(" / ")  # alternatives: "Empire / Imperial"
        if sec in ("Characters", "Places"):
            hit = any(f in en_text for f in forms)
        else:
            hit = any(f.lower() in en_text.lower() for f in forms)
        if not hit:
            errs.append(f"glossary: {j} -> {en} missing")
    for j, en in names.items():
        for h, eh in HONORIFICS.items():
            if j + h in e["jp"] and en + eh not in en_text:
                errs.append(f"honorific: {j}{h} -> {en}{eh} missing")
    return errs


def load_out(name):
    path = TL / f"{name}.out.tsv"
    if not path.exists():
        return None, [f"{path.relative_to(ROOT)} missing"]
    out, errs = {}, []
    for row in read_tsv(path):
        if len(row) != 2:
            errs.append(f"{row[0]}: {len(row)} tab-separated fields, want 2 (id, English)")
            continue
        if row[0] in out:
            errs.append(f"{row[0]}: duplicate id")
        out[row[0]] = row[1]
    return out, errs


def check(names):
    ents, gl, data, w = entries_by_id(), glossary(), windows.load(), font.widths()
    allowed = set(w) | {" "}
    total = 0
    for name in names:
        ids = [r[0] for r in read_tsv(TL / f"{name}.tsv")]
        out, errs = load_out(name)
        if out is not None:
            if missing := [i for i in ids if i not in out]:
                errs.append(f"missing ids: {' '.join(missing)}")
            if extra := [i for i in out if i not in ids]:
                errs.append(f"extra ids: {' '.join(extra)}")
            for i in ids:
                if i in out:
                    errs += [f"{i}: {x}" for x in check_entry(ents[i], out[i], gl, data, w, allowed)]
        for x in errs:
            print(f"{name} {x}")
        print(f"{name}: {'OK' if not errs else f'{len(errs)} errors'}")
        total += len(errs)
    return 1 if total else 0


def merge(names):
    if check(names):
        sys.exit("not merged: fix the errors above")
    ents = entries_by_id()
    new = {}
    for name in names:
        new.update({i: compose(ents[i], t) for i, t in load_out(name)[0].items()})
    for path in sorted(build.extract.SCRIPT.glob("*.json")):
        es = json.loads(path.read_text(encoding="utf-8"))
        if not any(e["id"] in new for e in es):
            continue
        for e in es:
            if e["id"] in new:
                e["en"] = new[e["id"]]
        path.write_text(json.dumps(es, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {len(new)} entries")


def pairs(name):
    out = load_out(name)[0] or {}
    rows = []
    for r in read_tsv(TL / f"{name}.tsv"):
        rows.append(f">> {r[0]} | {r[1]} | {r[4]}\n   {out.get(r[0], '(missing)')}")
    path = TL / f"{name}.pairs.txt"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(path.relative_to(ROOT), len(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["split", "check", "merge", "pairs"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--chars", type=int, default=3500)
    a = ap.parse_args()
    if a.cmd == "split":
        split(a.args, a.chars)
    elif a.cmd == "check":
        sys.exit(check(a.args))
    elif a.cmd == "merge":
        merge(a.args)
    else:
        for n in a.args:
            pairs(n)


if __name__ == "__main__":
    main()
