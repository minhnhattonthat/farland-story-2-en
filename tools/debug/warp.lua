-- Farland Story 2 warp: cold boot (or a state saved by an earlier warp) -> any scene in scenes.lua.
-- Globals (emu.py --var):
--   SCENE='ch05'   scene name (required)
--   SCENES='path'  scene list (default <repo>/tools/debug/scenes.lua)
--   DONE_STATE='abs path.mss'  save a state when the scene is reached
--   FAST=1         text print speed pinned to the fastest
--   GOD=1          party HP pinned to max every frame
--   HOLD=3000      after the scene is reached, keep clicking A for this many frames (text tours), then stop
--   CLICK=0        with HOLD: wait without clicking (shots of one page)
-- When the scene is reached: shot <out>/<SCENE>.png, log "warp reached", optional state, stop.
-- RAM (RE notes: docs/re/debug.md): $0292 outer mode (0 logos, 1 intro, 2 title menu, 7 game); $0293 game step
-- (9 New Game, 10-16 load chapter $03B1, 17 run it); $0294 battle sub-state (3 story, 5 phase banner, 6 map idle,
-- 7 map menu, 9 unit menu, 11-13 enemy phase); $036B menu depth; $0338/$0339 map cursor tile; title menu
-- cursor $0354 (0 = New Game); unit records $7F0000 + 60*i (i < 19 party): +1 x, +2 y, +$22 max HP, +$24 HP.
-- Mesen's cwd is its own folder: find the repo root from the ROM path (rom/ or build/ sit in the root).
local root = emu.getRomInfo().path:gsub("\\", "/"):match("^(.*)/[^/]+/[^/]+$")
local W = { scenes = dofile(SCENES or (root .. "/tools/debug/scenes.lua")) }
WARP = W
if SCENE == "__list" then  -- for tools/debug/regen.py: one "scene <name> <map|cold>" line each
  for name, s in pairs(W.scenes) do L.log("scene " .. name .. " " .. (s.map and "map" or "cold")) end
  L.finish(0)
  return
end
local sc = W.scenes[SCENE]
if not sc then error("unknown SCENE " .. tostring(SCENE)) end
W.scene = sc
-- English builds move strings: <rom>.reloc.txt (tools/build.py) maps a Japanese string address to its new one
do
  local f = io.open((emu.getRomInfo().path:gsub("%.%w+$", ".reloc.txt")), "r")
  if f then
    for line in f:lines() do
      local o, n = line:match("^(%x+) (%x+)")
      if o and tonumber(o, 16) == sc.text then sc.text = tonumber(n, 16) end
    end
    f:close()
  end
end
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local function r16(a) return r(a) | (r(a + 1) << 8) end
local function w(a, v) emu.write(a, v, emu.memType.snesWorkRam) end
W.r, W.r16, W.w = r, r16, w
function W.unit(i) return 0x10000 + i * 60 end  -- WRAM offset of unit record i ($7F0000 + 60*i)

function W.reached()
  if W.done then return end
  W.done = true
  L.shot(SCENE .. ".png")
  L.log(string.format("warp reached %s at frame %d", SCENE, L.frame))
  local finish = function() if HOLD then W.holdEnd = L.frame + HOLD else L.finish(0) end end
  if DONE_STATE then L.save_state(DONE_STATE, finish) else finish() end
end

-- Text: the draw loop $C0:2C53 reads the string at [$04C6] (24-bit) + offset $04CC; offset 0 = a new string.
W.text, W.textFrame = nil, -10
L.on_exec(0xC02C53, 0xC02C53, function()
  if r16(0x4CC) ~= 0 then return end
  local p = r16(0x4C6) | (r(0x4C8) << 16)
  if p == W.text and L.frame - W.textFrame < 2 then W.textFrame = L.frame; return end
  if p ~= W.text or L.frame - W.textFrame > 30 then L.log(string.format("text f%d %06X", L.frame, p)) end
  W.text, W.textFrame = p, L.frame
end)

-- Scene exec trigger(s): W.hit is set when the game runs one of these addresses.
W.hit = false
for _, a in ipairs(type(sc.exec) == "table" and sc.exec or { sc.exec }) do
  L.on_exec(a, a, function() W.hit = true end)
end

-- Party for a warped chapter. The chapter loader ($C1:1811, step 11) reads one (x, y) pair from the chapter's
-- unit list ($C2:3656) per party member already in records 0-18, then the other units; a wrong party size
-- misparses the list and the loader hangs ($C1:18EE, $C1:19AB) or crashes. Chapter 0 builds the real party, so a
-- warp gives K copies of the hero record (ids 1..K) and searches K = 0..19: a state saved at New Game is reloaded
-- with the next K until step 11 ends within LOAD_LIMIT frames.
local HERO = { 0x01, 0x21, 0x10, 0x10, 0x02, 0x00, 0x01, 0x04, 0x30, 0, 0, 0, 0x02, 0x71, 0, 0, 0, 0, 0, 0, 0, 0x01,
  0x01, 0x00, 0x0A, 0x12, 0x08, 0x08, 0, 0, 0x04, 0x04, 0x06, 0x06, 0x2D, 0x2D, 0x2D, 0, 0, 0x01, 0x06, 0, 0, 0x0F,
  0x03, 0x0F }  -- record 0 on the stage 1 map after a real New Game (work/states/map.mss)
local LOAD_LIMIT = 300
local K, kState, loadSince = 0, OUT .. "_newgame.mss", nil
local function set_party()
  -- the table is only cleared by chapter 0: garbage would also leave no free slot
  for a = 0x10000, 0x10D1F do w(a, 0) end
  for i = 0, K - 1 do
    for j, v in ipairs(HERO) do w(W.unit(i) + j - 1, v) end
    w(W.unit(i) + 0x15, i + 1)
  end
end

-- New Game handler $C1:0280 does STZ $03B1 / STZ $03B3; overwrite both right after.
W.started = false
L.on_exec(0xC10288, 0xC10288, function()
  if W.started then return end
  if sc.chapter then
    local ch = sc.load or sc.chapter
    w(0x3B1, ch); w(0x3B3, ch)
    set_party()
    L.save_state(kState)
  end
  W.started = true
  L.log(string.format("warp %s: new game, chapter %d at frame %d", SCENE, sc.chapter or 0, L.frame))
end)
-- sc.load: chapters whose own unit list crashes the loader load chapter sc.load's map and units, then the chapter
-- stub call $C0:C9C3 (step 13) runs chapter sc.chapter's script instead.
if sc.load then
  L.on_exec(0xC0C9C3, 0xC0C9C3, function() w(0x3B1, sc.chapter) end)
end
local function chapter_load_watch()
  local step = r(0x293)
  if step == 11 then
    loadSince = loadSince or L.frame
    if L.frame - loadSince > LOAD_LIMIT then
      K = K + 1
      if K > 19 then L.log("warp failed: no party size loads chapter " .. sc.chapter); L.finish(0); return end
      loadSince = nil
      L.load_state(kState, set_party)
    end
  elseif step > 11 and loadSince then
    loadSince = false
    -- K = 0 leaves record 0 (the hero the story moves) with id 0, whose sprite is a garbage metasprite (pointer 0)
    -- that can overflow the sprite line limit and cut holes in portraits: give it the hero's id
    if K == 0 and r(W.unit(0) + 0x15) == 0 then w(W.unit(0) + 0x15, 1) end
    L.log(string.format("warp party size %d loads chapter %d", K, sc.chapter))
  end
end

function W.map_idle(ch) return r(0x3B1) == (ch or 1) and r(0x293) == 17 and r(0x294) == 6 end
local function click(n) if n % 10 == 0 then L.press("a", 6) end end
W.click = click
local stage, stageFrame, menuSince = "go", nil, nil

L.on_frame(function(n)
  if FAST then w(0x4CE, 0); w(0x4D0, 0) end
  if GOD or sc.god then
    for i = 0, 18 do local o = W.unit(i); if r(o + 0x24) > 0 then w(o + 0x24, r(o + 0x22)) end end
  end
  if W.done then  -- HOLD: keep clicking A through the scene's text, then stop
    if W.holdEnd then
      if CLICK ~= 0 then click(n) end
      if n >= W.holdEnd then L.finish(0) end
    end
    return
  end
  if sc.chapter and W.started and loadSince ~= false then chapter_load_watch() end
  if stage == "until" and sc.loop then sc.loop(W, n) end
  if not L.route_done() then return end
  local mode = r(0x292)
  if not W.started then
    if mode == 7 and n < 5 then W.started = true; return end  -- started from a state already in game
    if mode < 2 then  -- Start through logos and intro, then New Game on the title menu
      if n % 20 == 0 then L.press("start", 6) end
    elseif mode == 2 then
      menuSince = menuSince or n
      if sc.title then
        if n - menuSince >= 120 then W.reached() end
      elseif n - menuSince >= 60 and n % 20 == 0 then
        L.press(r(0x354) == 0 and "a" or "up", 6)
      end
    end
    return
  end
  if stage == "go" then  -- reach the scene's base condition
    if sc.map then  -- idle on the battle map, player phase
      if W.map_idle(sc.mapch) then stage = "after"
      elseif r(0x294) ~= 9 and r(0x293) >= 14 then click(n) end
    elseif sc.text then  -- a string starts drawing
      if W.text == sc.text then stage, stageFrame = "settle", W.textFrame else click(n) end
    elseif sc.exec then  -- the game runs an address
      if W.hit then stage, stageFrame = "settle", n else click(n) end
    elseif sc.chapter then  -- the chapter script is running
      if r(0x293) == 17 then stage = "after" elseif r(0x293) >= 14 then click(n) end  -- 14-16: card waits for A
    end
  elseif stage == "after" then  -- optional pokes and cursor move, then presses, then an end condition
    if sc.poke then sc.poke(W) end
    stage = sc.cursor and "cursor" or "route"
  elseif stage == "cursor" then
    local x, y, tx, ty = r(0x338), r(0x339), sc.cursor[1], sc.cursor[2]
    if x ~= tx then L.press(x < tx and "right" or "left", 6); L.press("-", 8)
    elseif y ~= ty then L.press(y < ty and "down" or "up", 6); L.press("-", 8)
    else L.press("-", 10); stage = "route" end
  elseif stage == "route" then
    for step in (sc.route or ""):gmatch("[^;]+") do
      local f, b = step:match("^%s*(%d+)%s+(%S+)%s*$")
      L.press(b, tonumber(f))
    end
    W.hit, stage = false, "until"
  elseif stage == "until" then
    local cond = sc["until"]
    if cond == nil or (cond == "hit" and W.hit) or (cond == "text" and W.text == sc.text)
      or (type(cond) == "function" and cond(W)) then
      stage, stageFrame = "settle", n
    end
  elseif stage == "settle" then
    if n - stageFrame >= (sc.settle or 60) then W.reached() end
  end
end)
