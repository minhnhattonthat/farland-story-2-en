-- QA: show command-menu labels no reachable menu offers yet (Warp, Special, Rally, Full Map, Unit List).
-- Copies label slot SRC[i] over slot DST[i] in the emulator's ROM copy at frame 0, so the next unit/map menu
-- draws it (slot layout: tools/gfx.py; slots 0-9 = 0xC0 bytes at 0xD45EB, 10-16 = 0x140 bytes at 0xD4D6B).
--   emu.py ROM --state-in map.mss --route-str "6 a;60 -" --script tools/lua/labelswap.lua --var "SWAP='1>0,2>5'"
local function slot(n)
  if n < 10 then return 0xD45EB + n * 0xC0, 0xC0 end
  return 0xD4D6B + (n - 10) * 0x140, 0x140
end
local done = false
L.on_frame(function()
  if done then return end
  done = true
  for src, dst in string.gmatch(SWAP or "", "(%d+)>(%d+)") do
    local s, n = slot(tonumber(src))
    local d, m = slot(tonumber(dst))
    assert(n == m, "slots of different sizes: " .. src .. ">" .. dst)
    for i = 0, n - 1 do
      emu.write(d + i, emu.read(s + i, emu.memType.snesPrgRom), emu.memType.snesPrgRom)
    end
    L.log("label slot " .. src .. " shown as " .. dst)
  end
end)
