# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-25 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (owner's standing answer for one-shot runs). |
| D2 | 2026-10-25 | Romanization source for names | official art, earlier patch, Hepburn | Official English where it exists, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-25 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-25 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; not contradicted). |
| D5 | 2026-10-25 | Graphics text left in Japanese | none (default), list | Translate all; keep the Japanese logo only if there is no official English logo. |
| D6 | 2026-10-25 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, one phase per session, commit + push to main. The run ends at a built, verified release zip; never publish a GitHub release or change repo visibility. |
| D7 | 2026-10-25 | Existing saves / savestates | user-supplied, none | None provided; build the debug tool (phase 2). |
| D8 | 2026-10-25 | Git identity | ask, preset | Preset by new-game.ps1; don't change it. |
| D9 | 2026-10-25 | Register and sound effects (not asked: pre-approved run, D6; controller default) | archaic / modern; romaji / English SFX | Modern natural fantasy English; English onomatopoeia, except voice tics (Gibogera "Gebohahaha!", Klaus "Rawr!"). Owner may override. |
| D10 | 2026-10-25 | Names the fan script spells oddly (Serena for サリーナ, Cifil, Ligito, Lodoss) and terms (破亡の舞) | Hepburn / fan spelling | D2 applied as written: fan spellings for names. Terms are translations, not names: 破亡の舞 = "Dance of Ruin" (fan "Dance of Death" misses 破亡 = destroy and perish). |
| D11 | 2026-10-25 | Box text line breaks | translators break lines / tool wraps | Tool: translators write one paragraph per page; `tools/wrap.py` breaks lines by pixel width at build time and adds pages when a page needs more than 3 lines. |
