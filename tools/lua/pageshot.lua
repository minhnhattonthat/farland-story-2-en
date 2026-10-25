-- Text tour, after tools/debug/warp.lua has reached its scene (needs HOLD and CLICK=0 so warp.lua stops
-- clicking): one shot per page that waits for a key ({wait}, handler $C0:310F runs every frame while waiting),
-- `page_<frame>.png`, then A. With no wait for 120 frames, A every 60 frames (scripted pauses, cards), but not
-- during camera / phase banner / map idle ($0294 = 4-6: A would open a unit menu). Stops when
-- the battle map goes idle for the player ($0293 = 17, $0294 = 6) or the warp's HOLD runs out.
--   regen.py chNN --hold 40000 --script tools/lua/pageshot.lua   (regen.py passes CLICK=0 with --pages)
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local lastWait, shotAt, pressAt, idle = -100, nil, nil, 0
local pages = 0
L.on_exec(0xC0310F, 0xC0310F, function()
  if L.frame - lastWait > 1 and not pressAt then shotAt = L.frame + (PAGE_DELAY or 3) end
  lastWait = L.frame
end)
L.on_frame(function(n)
  if not (WARP and WARP.done) then return end
  if shotAt and n >= shotAt then
    pages = pages + 1
    L.shot(string.format("page_%06d.png", n))
    shotAt, pressAt = nil, n + 2
  elseif pressAt and n >= pressAt then
    L.press("a", 6)
    pressAt = nil
  elseif not shotAt and not pressAt and n - lastWait > 120 and n % 60 == 0
    and not (r(0x293) == 17 and r(0x294) >= 4 and r(0x294) <= 6) then  -- no blind A once the map takes over
    L.press("a", 6)
  end
  if r(0x293) == 17 and r(0x294) == 6 then idle = idle + 1 else idle = 0 end
  if idle == 60 then
    L.shot(string.format("page_%06d.png", n))
    L.log(string.format("pageshot: map idle at frame %d after %d pages", n, pages))
    L.finish(0)
  end
end)
