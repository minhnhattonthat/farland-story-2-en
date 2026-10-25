# Translator brief - Farland Story 2 (SNES, TGL, 1995)

You translate part of the Japanese script of Farland Story 2 into English for a fan patch. A light-hearted fantasy
strategy RPG: Prince Riad flees his father's Valdes Empire with Serena, a girl the Empire wants for her power, and
gathers allies; King Ark of Felsaria (hero of the first game) joins later. Bright, earnest, with comic monsters.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs (chapters 0-1). Match this voice.
2. `work/tl/<batch>.terms.txt` - binding glossary rows for this batch (full table in `glossary.md` if you need more).
3. `docs/synopsis.md` - plot, who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>box<TAB>form<TAB>limit<TAB>Japanese`, in story order (use neighbours for context; there are no speaker
names: `box` upper/lower is which portrait window speaks, and two boxes usually alternate between two speakers;
work out who from the content, the synopsis and the neighbours).
- form `dlg`: one speech. The Japanese gives its pages (one key press each) separated by ` || `. Write the same
  number of English pages, separated by ` || `, each page one paragraph with no line breaks: a tool wraps lines
  and adds pages by pixel width, so you don't count characters. Keep each page about as long as the Japanese
  page reads (2-3 short sentences); a page's English may run long when the meaning needs it.
- form `layout`: menus, item descriptions, credits, stage cards, system messages. The Japanese is shown with its
  control codes (`{pos:..}`, `{half}`, `{full}`, `{clr}`, `{delay:..}`, `{spd1}`, `{f40on}` ...). Copy every code
  except `{nl}` in the same order; `{nl}` (line break) you may move or drop. Every line must fit `limit`
  (`63px x1` = one line of at most 63 pixels; roughly 5 px a lowercase letter, 7-9 a capital or m/w, 4 a space).
  `　` (full-width space, 6 px) may be used for alignment, as the Japanese does.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--` is drawn as
an em dash only if you write the character `—` (allowed), `…` is not needed (write `...`). Allowed besides ASCII:
`—` `♪` `　`. No tabs inside the English, no Japanese or other non-ASCII, no `\uXXXX`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints
`<batch>: OK`. `python -X utf8 tools/wrap.py "{clr}your page{wait}"` shows how a page wraps (lines with pixel
widths); three lines make a window page.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Names and terms exactly as in the glossary (the check enforces names and places). Full names and terms, never
  abbreviated. If a `layout` line can't fit its limit without losing meaning, keep the meaning, report `LONG: id`.
- Honorifics kept, hyphenated after the glossary name: アークさま -> Ark-sama, リアドさん -> Riad-san, くん -kun,
  ちゃん -chan, どの -dono. Titles that are words translate: 王さま "the king"/"Your Majesty", 父上 "Father",
  姫 "Princess", 隊長 "Captain". Western name order.
- Punctuation: 「」 -> "...", 『』 -> '...' (titles, quoted names), ・・・/… -> `...`, ！？ -> `?!`, ー (long
  vowel in a cry) -> repeat the letter, ～ -> `~` only in a playful/sing-song line.
- Sound effects and cries in English: グルル -> "Grrr...", ガオー -> "Raaargh!", ワン -> "Woof!", フッ -> "Heh."
  (a smirk), ハハハ -> "Hahaha!". Laughs and grunts as English sounds, not romaji.
- American spelling (rumor, neighbor, color, armor).
- Register: modern, natural fantasy English; no archaic "thee/thou" unless the Japanese is archaic (a dragon,
  an ancient spirit may be formal). Villains can be grandiose; comic monsters comic. Keep each character's voice
  from the style reference (rough/polite/childish/old-man speech).
- Stats as in the glossary: ＨＰ HP, 攻撃力 Attack, 間せつ攻撃力 Ranged Attack, 魔法力 Magic, Ｐぼうぎょ Defense,
  Ｍぼうぎょ Resistance, 素早さ Speed, 移動力 Move, 最大体力 Max HP; "Attack +4" for 攻撃力＋４; ３ＵＰ -> "+3".
  Full-width digits and letters -> ASCII. Item names inside text exactly as in `script/items.json` `en`.
- Item descriptions (item_desc): line 1 the effect, then who can equip it - the Japanese lists names separated
  by ・; write them with commas ("Riad, Valakana, Cifil"). Keep `{half}`/`{full}` where they are.
- No suffix glued to a number the game fills in; no "a/an" right before a name.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Notes from earlier batches
- (added by the controller between waves)

## Report (reply with only this)
Files written and entry count per batch; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`,
`LONG: id - note`.
