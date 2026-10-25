-- Log every string the text engine starts, with its window: "str f<frame> <ptr> win=<$04BF> w=<$04D3 cells>
-- h=<$04D4 lines> mode=<$04CA> [buf=<hex words>]". Strings drawn from RAM (menus and messages are built in a
-- buffer such as $7E:F8D6 first) carry their bytes, so tools/windows.py can match them to script entries.
--   emu.py ... --script tools/lua/textlog.lua
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local function r16(a) return r(a) | (r(a + 1) << 8) end
local seen = {}
L.on_exec(0xC02C53, 0xC02C53, function()
  if r16(0x4CC) ~= 0 then return end
  local p = r16(0x4C6) | (r(0x4C8) << 16)
  local k = string.format("%06X win=%02X w=%d h=%d mode=%02X", p, r(0x4BF), r(0x4D3), r(0x4D4), r(0x4CA))
  if p >= 0x7E0000 and p < 0x800000 then
    local hex, a = {}, p - 0x7E0000
    for i = 0, 255, 2 do
      local w = r16(a + i)
      hex[#hex + 1] = string.format("%02X%02X", w & 0xFF, w >> 8)
      if w == 0x8000 then break end
    end
    k = k .. " buf=" .. table.concat(hex)
  end
  if not seen[k] then
    seen[k] = true
    L.log(string.format("str f%d %s", L.frame, k))
  end
end)
