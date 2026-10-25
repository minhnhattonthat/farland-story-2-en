-- Where did the code go? Two modes (SNES, Mesen):
--   --var FROM=230 --var TO=260 --var "BANKS={0xC1,0xEB}"  every PC run in those banks in the frame window,
--       sorted, to <out>/trace.txt (find which routines build a menu or screen)
--   --var STOPPC=0x00FE54  the last 80 PCs (tight loops collapsed) before the first run of STOPPC, to log.txt
--       (how a hang or crash was entered)
if STOPPC then
  local hist, done, last = {}, false, -1
  emu.addMemoryCallback(function(a)
    if done then return end
    if a == STOPPC then done = true; L.log("history: " .. table.concat(hist, " ")); return end
    if a < last or a > last + 4 then
      hist[#hist + 1] = string.format("%06X", a)
      if #hist > 80 then table.remove(hist, 1) end
    end
    last = a
  end, emu.callbackType.exec, 0, 0xFFFFFF, emu.cpuType.snes, emu.memType.snesMemory)
  return
end
local seen = {}
local function hit(a) if L.frame >= FROM and L.frame <= TO then seen[a] = true end end
for _, b in ipairs(BANKS) do
  emu.addMemoryCallback(hit, emu.callbackType.exec, b << 16, (b << 16) | 0xFFFF, emu.cpuType.snes, emu.memType.snesMemory)
end
L.on_frame(function(n)
  if n ~= TO + 1 then return end
  local t = {}
  for a in pairs(seen) do t[#t + 1] = a end
  table.sort(t)
  local f = assert(io.open(OUT .. "trace.txt", "w"))
  for _, a in ipairs(t) do f:write(string.format("%06X\n", a)) end
  f:close()
end)
