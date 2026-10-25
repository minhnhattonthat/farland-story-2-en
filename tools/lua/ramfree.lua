-- Which low-WRAM bytes ($0000-$1FFF) are never written? Logs the unwritten runs of >= 4 bytes every 1000 frames
-- ("free <lo>-<hi>"); intersect several runs (dialogue, menus, battle) before using one for patch variables.
--   emu.py ... --script tools/lua/ramfree.lua
local written = {}
L.on_write(0x0000, 0x1FFF, function(addr) written[addr & 0x1FFF] = true end)
L.on_frame(function(n)
  if n % 1000 ~= 0 then return end
  local runs, start = {}, nil
  for a = 0, 0x2000 do
    if a < 0x2000 and not written[a] then start = start or a
    elseif start then
      if a - start >= 4 then runs[#runs + 1] = string.format("%04X-%04X", start, a - 1) end
      start = nil
    end
  end
  L.log("f" .. n .. " free " .. table.concat(runs, " "))
end)
