# Visual-QA reviewer brief - Farland Story 2 (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/p8/verdicts/<chunk>.tsv` (the dispatch names it).
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Farland Story 2:
  - `view/` sheets come from a string viewer: dialogue that only plays mid- or post-battle is drawn in another
    chapter's story box, so the portrait, speaker and map belong to that host scene. Judge only the text.
  - Warped chapters 20 and 34-38 show chapter 19's / 33's map; warped chapters have stand-in party units.
  - The katakana title logo ファーランドストーリー stays Japanese (decision D5); the English "FARLAND STORY 2"
    sub-logo is the game's own.
  - Two dialogue boxes (upper and lower) are both on screen; the one not speaking is empty or holds the last line.
  - A ▼ arrow at the bottom right of a box is the page-wait prompt.
  - STAGE cards and the objective window use the full-width layout of the original ("STAGE 01", "- Objective -").
  - Line and page breaks come from `tools/wrap.py`: a one-word last line is fine when moving one more word down
    would not fit, and a page break may fall mid-sentence where the jp field breaks the page there too. A page
    holding a single leftover line or word of an overflowing paragraph is an issue.
  - `scenes/` sheets pair each scene: English build left, original ROM right (one shot per warp scene; a box
    still typing in either is not a bug). `tour/` and `view/` sheets: one shot per page wait; the same page can
    appear twice in a row.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
