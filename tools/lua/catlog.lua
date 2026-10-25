-- Log the string concatenations of $C2:28BA (append [$14] to the string at [$10]): "cat f<frame> dst=<$10>
-- src=<$14> dstlen=<bytes already there>". Finds RAM-buffer overflows (the $7E:F8D6 buffers are 256 bytes).
--   emu.py ... --script tools/lua/catlog.lua
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local function r24(a) return r(a) | (r(a + 1) << 8) | (r(a + 2) << 16) end
local start
L.on_exec(0xC228BA, 0xC228BA, function() start = r24(0x10) end)
L.on_exec(0xC228D4, 0xC228D4, function()
  local src = r24(0x14)
  local n = 0  -- source length in bytes (up to 512)
  if src >= 0x7E0000 and src < 0x800000 then
    while n < 512 and (r(src - 0x7E0000 + n) | (r(src - 0x7E0000 + n + 1) << 8)) ~= 0x8000 do n = n + 2 end
  end
  L.log(string.format("cat f%d dst=%06X src=%06X dstlen=%d srclen=%d", L.frame, start or 0, src,
    r24(0x10) - (start or 0), n))
end)
