-- Scene list for warp.lua: name -> how to get there from a cold boot. Fields:
--   chapter = N   New Game with the chapter script index $03B1 (= $03B3) set to N (0-38, table $C0:C9F0): the
--                 chapter plays as if the previous one had just ended (its story, STAGE card, battle). Warped
--                 chapters have no party (it joins in chapter 0's script), so battle-map scenes use `map`.
--   map = true    real New Game clicked through to the first player phase of stage 1, cursor on the hero.
--   text = $BBAAAA  click A until this string starts drawing (base condition, or with until = "text").
--   poke = fn(W)  RAM writes once the base condition holds; cursor = {x, y}: move the map cursor there.
--   route = "6 a;30 -"  presses (frames buttons) after that; until = "hit" (game ran an address in `exec`),
--                 "text", or fn(W) -> bool; loop = fn(W, n) runs every frame while waiting; settle = frames
--                 to wait before the shot (default 60).
-- Party/hero: unit record 0 at (33,16) on the stage 1 map; menus open on A (unit) and B (map).
local S = {
  title = { title = true },
}
-- load = M: these chapters' own unit lists crash the loader without the real party (docs/re/debug.md), so they
-- load chapter M's map and units and run their own script on it.
local LOAD = { [20] = 19, [34] = 33, [35] = 33, [36] = 33, [37] = 33, [38] = 33 }
for n = 0, 38 do S[string.format("ch%02d", n)] = { chapter = n, load = LOAD[n], settle = 240 } end

-- STAGE cards: stage -> {chapter, card string}. Chapters 0, 6, 8, 9, 13, 23, 31-38 have no card.
local cards = {
  { 1, 0xC49BF3 }, { 2, 0xC62500 }, { 3, 0xC63F8D }, { 4, 0xC6550A }, { 5, 0xC66656 }, { 7, 0xC686A7 },
  { 10, 0xC6BCF7 }, { 11, 0xC6D14B }, { 12, 0xC6DBBF }, { 14, 0xC6F9C6 }, { 15, 0xC50F44 }, { 16, 0xC52430 },
  { 17, 0xC54422 }, { 18, 0xC5626A }, { 19, 0xC57036 }, { 20, 0xC584E2 }, { 21, 0xC59198 }, { 22, 0xC59C0A },
  { 24, 0xC5B77C }, { 25, 0xC5BEE5 }, { 26, 0xC5D266 }, { 27, 0xC5E45A }, { 28, 0xC5F2FC }, { 29, 0xC5FC77 },
  { 30, 0xEA3E0D },
}
for stage, c in ipairs(cards) do
  S[string.format("stage%02d", stage)] = { chapter = c[1], load = LOAD[c[1]], text = c[2], settle = 90 }
end

-- Battle map (stage 1, real party)
local function M(t) t.map = true; return t end
local function menu_open(W) return W.r(0x36B) > 0 end
S.map = M {}
S.phase_banner = { exec = 0xC10B0B, settle = 30 }                         -- "リアドたちの行動" player phase
S.unit_menu = M { route = "6 a;10 -", ["until"] = menu_open, settle = 40 }  -- 移動 武器 アイテム 交換
S.move_range = M { route = "6 a;40 -;6 a;60 -" }
S.standby = M { route = "6 a;40 -;6 a;60 -;6 down;20 -;6 down;20 -;6 a;10 -", ["until"] = menu_open }  -- post-move 待機
S.weapons = M { route = "6 a;40 -;6 down;20 -;6 a" }
S.items = M { route = "6 a;40 -;6 down;20 -;6 down;20 -;6 a" }
S.item_use = M { route = "6 a;40 -;6 down;20 -;6 down;20 -;6 a;80 -;6 a" }  -- つかう / うる
S.exchange = M { route = "6 a;40 -;6 down;20 -;6 down;20 -;6 down;20 -;6 a;40 -;6 up;20 -;6 a" }  -- with unit 1 above
S.unit_status = M { route = "6 y;10 -", ["until"] = menu_open }            -- Y on a unit: status window
S.enemy_status = M { cursor = { 39, 19 }, route = "6 y;10 -", ["until"] = menu_open }
-- Shop: the pre-move menu offers 店 when the unit stands on a shop tile of the chapter's list ($C3:22A6;
-- stage 1 has (32,18)). Only the record's x/y is moved, not the sprite: enough for the menu and shop window.
local function to_shop(W) W.w(W.unit(0) + 1, 32); W.w(W.unit(0) + 2, 18) end
S.shop_menu = M { poke = to_shop, route = "6 a;10 -", ["until"] = menu_open, settle = 40 }
-- Menu with the shop: 移動 買物 武器 アイテム 交換; the shop state machine is menu type $029B = 5.
local function in_shop(W) return W.r(0x29B) == 5 end
S.shop = M { poke = to_shop, route = "6 a;40 -;6 down;20 -;6 a;10 -", ["until"] = in_shop, settle = 90 }
S.shop_buy = M { poke = to_shop, route = "6 a;40 -;6 down;20 -;6 a;90 -;6 a;10 -", ["until"] = in_shop, settle = 90 }
S.shop_nomoney = M { poke = to_shop, route = "6 a;40 -;6 down;20 -;6 a;90 -;6 a;60 -;6 a;10 -", ["until"] = in_shop,
  settle = 40 }                                                             -- おかねがたりません！ (0 gold)
S.map_menu = M { route = "6 b;10 -", ["until"] = menu_open, settle = 40 }  -- ターン終了 状況 セーブ ロード 環境設定
S.objective = M { route = "6 b;40 -;6 down;20 -;6 a" }                    -- 状況: STAGE + objective
S.save = M { route = "6 b;40 -;6 down;20 -;6 down;20 -;6 a" }
S.save_confirm = M { route = "6 b;40 -;6 down;20 -;6 down;20 -;6 a;120 -;6 a" }
S.load = M { route = "6 b;40 -;6 down;20 -;6 down;20 -;6 down;20 -;6 a" }
S.settings = M { route = "6 b;40 -;6 up;20 -;6 a" }
-- Phase banners: copied to a RAM buffer before drawing, so caught by the code that loads them.
S.enemy_banner = M { route = "6 b;40 -;6 a", exec = 0xC10DE8, ["until"] = "hit", settle = 30 }  -- "帝国の行動"
-- Enemy phase: the first enemy attack opens the battle scene; $C1:E96A prints "<name>のこうげき！".
S.battle = M { route = "6 b;40 -;6 a", exec = 0xC1E96A, ["until"] = "hit", settle = 40, god = true,
  loop = function(W, n) if L.route_done() then W.click(n) end end }
-- Game over: party HP held at 1, End Turn every player phase; GAME OVER window built at $C3:09BA / $EA:0F98.
S.gameover = M { exec = { 0xC309BA, 0xEA0F98 }, ["until"] = "hit", settle = 90,
  loop = function(W, n)
    for i = 0, 18 do local o = W.unit(i); if W.r(o + 0x24) > 1 then W.w(o + 0x24, 1) end end
    if not L.route_done() then return end
    if W.r(0x293) == 17 and W.r(0x294) == 6 then L.press("-", 20); L.press("b", 6); L.press("-", 40); L.press("a", 6)
    else W.click(n) end
  end }

-- Ending: chapter 38 is the last script; the staff roll and THE END are its strings.
S.ending = { chapter = 38, load = 33, settle = 300 }
S.credits = { chapter = 38, load = 33, text = 0xEA723A, settle = 60 }
S.the_end = { chapter = 38, load = 33, text = 0xEA764E, settle = 120 }
return S
