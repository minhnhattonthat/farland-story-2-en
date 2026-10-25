-- Log Farland Story 2's game state on every change: chapter $03B1, step $0293, battle sub-state $0294, window
-- depth $036B, map cursor $0338/$0339 (meanings: docs/re/debug.md).  emu.py ... --script tools/lua/statelog.lua
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local last = ""
L.on_frame(function(n)
  local k = string.format("mode=%d ch=%d step=%d sub=%d menu=%d cur=%d,%d", r(0x292), r(0x3B1), r(0x293), r(0x294),
    r(0x36B), r(0x338), r(0x339))
  if k ~= last then last = k; L.log("f" .. n .. " " .. k) end
end)
