-- String viewer: once tools/debug/warp.lua has reached its scene, every string the game starts drawing from ROM
-- is swapped for the next one of VIEW (lines "<id> <hex CPU address>", tools/coverage.py --missing), lines
-- FIRST..LAST. Logs "view <id> f<frame> <addr>"; with tools/lua/pageshot.lua each page gets a shot. Stops when
-- the game starts a string after the last one. Run by tools/viewer.py.
local function r(a) return emu.read(a, emu.memType.snesWorkRam) end
local function r16(a) return r(a) | (r(a + 1) << 8) end
local function w(a, v) emu.write(a, v, emu.memType.snesWorkRam) end
local list = {}
for line in io.lines(VIEW) do
  local id, a = line:match("^(%S+) (%x+)")
  if id then list[#list + 1] = { id, tonumber(a, 16) } end
end
local i, last, cur = FIRST or 1, math.min(LAST or #list, #list), nil
L.on_exec(0xC02C53, 0xC02C53, function()
  if not (WARP and WARP.done) or r16(0x4CC) ~= 0 then return end
  local p = r16(0x4C6) | (r(0x4C8) << 16)
  if p == cur or (p >= 0x7E0000 and p < 0x800000) then return end  -- the swapped string; RAM buffers
  if i > last then
    L.log(string.format("viewer: done at frame %d", L.frame))
    L.finish(0)
    return
  end
  cur = list[i][2]
  w(0x4C6, cur & 0xFF); w(0x4C7, (cur >> 8) & 0xFF); w(0x4C8, cur >> 16)
  L.log(string.format("view %s f%d %06X", list[i][1], L.frame, cur))
  i = i + 1
end)
