-- Dump the unit table $7F0000 (56 records x 60 bytes; 0-18 party) to log.txt at frame AT (default 10).
--   emu.py ... --script tools/lua/unitdump.lua --var AT=400
L.on_frame(function(n)
  if n ~= (AT or 10) then return end
  for i = 0, 55 do
    local t = {}
    for j = 0, 59 do t[#t + 1] = string.format("%02X", emu.read(0x10000 + i * 60 + j, emu.memType.snesWorkRam)) end
    L.log(string.format("%2d %s", i, table.concat(t, " ")))
  end
end)
