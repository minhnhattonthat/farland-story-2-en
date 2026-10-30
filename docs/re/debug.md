# Debug tool: game state, warps, scene list

`tools/debug/warp.lua` + `tools/debug/scenes.lua` reach every scene from a cold boot; `tools/debug/regen.py` runs
them all and keeps a shot and a savestate of each (`work/qa/warp/shots/`, `work/states/<scene>.mss`).

```
python -X utf8 $SKILL/scripts/emu.py ROM --out work/qa/warp/x --script tools/debug/warp.lua --var "SCENE='stage05'" --frames 20000
python -X utf8 tools/debug/regen.py [SCENE ...] [--rom build/farland2_en.sfc] [--cold]
```

Warp globals: `SCENE`, `DONE_STATE` (state path), `FAST` (print speed pinned to 0; saves little, the slow parts
are scripted waits), `GOD` (party HP pinned to max). Battle-map scenes start from `work/states/map.mss` in
regen.py (made by the `map` scene from a cold boot first); `--cold` boots each one cold instead (~10000 frames).

Probes (`--script`): `tools/lua/statelog.lua` (state changes below), `tools/lua/unitdump.lua` (unit table),
`tools/lua/pctrace.lua` (PCs run in a frame window, or the path into a hang/crash).

## Game state (verified: RAM logs and pokes, `work/qa/steps1`, `sub1`, warps)

| RAM | Meaning |
|---|---|
| `$0292` | outer mode: 0 logos, 1 intro, 2 title menu, 3 title choice made, 6/7 game (title choice handlers `$C1:0176` New Game -> step 8; `$C1:0183` -> step 6, guess: Continue) |
| `$0293` | game step, dispatcher `$C1:01DA`, table `$C1:01F5`: 9 New Game (`$C1:0280`: `STZ $03B1/$03B3`), 10-16 load the chapter, 13 runs the chapter stub (`$C0:C9C3`), 17 chapter running (`$C1:05CB` -> battle sub-dispatcher) |
| `$0294` | battle sub-state, table `$C1:092B`: 3 story on the map, 4 camera, 5 phase banner, 6 map idle (player cursor), 7 map menu, 8 A pressed, 9 unit menu / unit selected, 10 deselect, 11-13 end turn + enemy phase, 14 new turn, 15 status window (Y) |
| `$036B` | open window depth (0 = none) |
| `$0354` | menu cursor (title menu: 0 = New Game) |
| `$0338/$0339` | map cursor tile x/y (`$033A/$033C` pixel, cursor code `$EB:0983-0A1D`) |
| `$03B1`, `$03B3` | chapter script index (always equal: `INC` both at chapter end, VM handler `$C0:E6A8`; loaded from the save at `$C1:246E`) |
| `$03B5` | 1 = resume a battle from a save |
| `$029B` | unit-command action (5 = shop, `$C1:2A10` dispatcher); `$0299` its sub-state |
| `$04C6-$04C8`, `$04CC` | current string pointer + offset (draw loop `$C0:2C53`); `$04CE/$04D0` print speed |
| `$7F0000 + 60*i` | unit records, i < 19 party (record 0 = the hero, リアド), 19+ others: +0 acted flag, +1/+2 tile x/y, +3/+5 pixel x/y, +4 character id (name table `$C2:45E3`), +$15 id class (< `$14` party), +$22/$23 max HP, +$24 HP (0 = down). Unit at a tile: `$EB:137D` |
| `$7EB8C3 + y*w + x` | tile map of units: record + 1 (0 = empty), w = map width `$7F0D90` (`$EB:11C4`); moving a unit means its record and this byte (`scenes.lua` `foe_below`) |

Chapter map: chapter 0 = prologue (the party joins in its script), chapter N shows STAGE N's card for 1-5, then
7 -> 6, 10 -> 7, 11 -> 8, 12 -> 9, 14-22 -> 10-18, 24-30 -> 19-25 (card strings listed in `scenes.lua`);
chapter 38 holds the staff roll (`$EA:723A`) and THE END (`$EA:764E`).

Warping a chapter = New Game with `$03B1/$03B3` overwritten right after `$C1:0288`: the chapter's own story, card
and battle play. Chapter 0 builds the real party, so a warp has to stand in for it:

- The unit table `$7F0000-$7F0D1F` is garbage until chapter 0 clears it; the warp zeroes it.
- The chapter loader (`$C1:1811`, step 11) reads the chapter's unit list (`$C2:3656`, 3-byte pointer per chapter):
  first one (x, y) pair per party member already in records 0-18, then the units (id < `$14` joins the party).
  A wrong party size misparses the list: hang at `$C1:18EE` (no free slot) / `$C1:19AB`, or a crash. The warp
  writes K copies of the hero record and searches K = 0..19, reloading a state saved at New Game, until step 11
  ends within 300 frames (log line "warp party size K loads chapter N"; e.g. ch06 K=7, ch11 K=11, ch17 K=5).
- Chapters 20 and 34-38 crash for every K (a scheduler task pointer gets corrupted: `$C1:0031` jumps into data).
  They use `load = M`: chapter M's map and units load, and the stub call `$C0:C9C3` runs chapter N's script
  (`scenes.lua` `LOAD`). Their text, card and credits play; the map behind them is chapter M's.
- The dummies are not the real cast, so battle menus, battles and the shop are reached from a real New Game
  instead (`map` scene: stage 1, first player phase, ~9600 frames with 10-frame A clicks).

## Menus and controls (stage 1 map)

- A on a party unit: unit menu 移動 / 武器 / アイテム / 交換 (+ 買物 on a shop tile, + other actions per unit:
  builder `$EB:0FB8`, action ids 1 move, 3/4 attacks, 5 shop, 6-8 ...). After a move: 待機 (+ 攻撃 next to an enemy,
  `$C1:2B00`). Y on any unit: status window. B: map menu ターン終了 / 状況 / セーブ / ロード / 環境設定.
- Shop: the unit menu offers 買物 when the unit stands on a tile of the chapter's shop list (`$C3:22A6`, word
  pointer per chapter to (x, y) byte pairs, `$FF` end; check `$EB:1ED4`). Chapters with shops: 1, 3, 4, 6, 9, 14,
  16-18, 21-23, 25, 26, 29. The warp moves only the hero's record x/y onto (32,18).
- Battle scene: enemy phase after End Turn; `$C1:E96A` prints "<name>のこうげき！".
- Game over: hero down -> GAME OVER window (`$C3:09BA` / `$EA:0F98`, strings `$C3:0A16` / `$EA:0FF4`), then the
  game resets to the logos.
- Phase banners "リアドたちの行動" / "帝国の行動" are inline strings `$C1:0B44` / `$C1:0E21`, copied to the RAM buffer
  `$7E:F8D6` before drawing (so the text log shows the buffer address, not the ROM one).

## Not covered yet (add when a later phase needs them)

- Special (必殺): scenes `special_menu` / `special` (stage 1 foe record 22 moved below the hero; the hero's
  Break Storm plays). Offered when Attack is (a foe in range, `$C3:0000`) and `$EB:1088` passes: class 1 HP >= 21,
  class 6 at full HP, class 9 ...
- Bongo's menu label list also has Warp, Gather, World Map, Unit: commands that appear in later
  chapters or with other units. Warped chapters have no party, so these need a save fixture or a party injection.
- Level-up, item-get and other post-battle messages (`$C1:F1BE` ...): seen only when a fight is won.
- Continue / load from the title (needs a save: `save_confirm` writes one in `<out>/` SRAM).
