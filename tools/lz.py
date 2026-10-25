"""Farland Story 2 LZ codec (decompressor at $C0:167D, docs/re/compression.md).

Block: u16 LE length of the packed stream (bytes after this header), then groups of one flag byte + 8 items,
flag bits LSB first. Bit set = copy: count byte, offset byte; copies count+1 bytes from ring[(pos + offset) & $FF],
byte by byte (overlap allowed). Bit clear = one literal byte. Ring: 256 bytes, zero-filled, write index starts at 0.
Decoding stops when the read index reaches the length, even mid-group.

    python -X utf8 tools/lz.py unpack ROM OFFSET OUT     # writes the unpacked bytes, prints packed size
    python -X utf8 tools/lz.py selftest
"""
import sys


def decompress(data, pos=0):
    """Returns (unpacked bytes, packed size including the 2-byte header)."""
    end = data[pos] | data[pos + 1] << 8
    src = data[pos + 2:pos + 2 + end]
    ring, rp, out, i = bytearray(256), 0, bytearray(), 0
    while i < end:
        flags = src[i]
        i += 1
        for bit in range(8):
            if i >= end:
                break
            if flags >> bit & 1:
                count, off = src[i], src[i + 1]
                i += 2
                s = (off + rp) & 0xFF
                for _ in range(count + 1):
                    b = ring[s]
                    out.append(b)
                    ring[rp] = b
                    rp = (rp + 1) & 0xFF
                    s = (s + 1) & 0xFF
            else:
                b = src[i]
                i += 1
                out.append(b)
                ring[rp] = b
                rp = (rp + 1) & 0xFF
    return bytes(out), end + 2


def compress(data):
    """Greedy encoder; the ring holds the last 256 output bytes, so offset = (match_pos - pos) & $FF."""
    ring_hist = bytearray(256)  # virtual: zero-filled history before the start
    buf = bytes(ring_hist) + bytes(data)
    out, items, flags, n, p = bytearray(), bytearray(), 0, 0, 0
    groups = []
    while p < len(data):
        best_len, best_off = 0, 0
        cur = 256 + p
        for back in range(1, 257):
            s = cur - back
            if s < 0:
                break
            ln = 0
            while ln < 256 and p + ln < len(data) and buf[s + ln] == buf[cur + ln]:
                ln += 1
            if ln > best_len:
                best_len, best_off = ln, (256 - back) & 0xFF
        if best_len >= 3:
            flags |= 1 << n
            items += bytes([best_len - 1, best_off])
            p += best_len
        else:
            items.append(data[p])
            p += 1
        n += 1
        if n == 8:
            groups.append(bytes([flags]) + items)
            flags, n, items = 0, 0, bytearray()
    if n:
        groups.append(bytes([flags]) + items)
    for g in groups:
        out += g
    return len(out).to_bytes(2, "little") + out


def selftest():
    import random
    rnd = random.Random(1)
    for k in range(50):
        data = bytes(rnd.choice(b"\x00\x00\x01ab") for _ in range(rnd.randint(0, 2000)))
        assert decompress(compress(data))[0] == data, k
    print("lz selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        selftest()
    elif sys.argv[1:2] == ["unpack"]:
        rom = open(sys.argv[2], "rb").read()
        out, size = decompress(rom, int(sys.argv[3], 16) & 0x3FFFFF)
        open(sys.argv[4], "wb").write(out)
        print(f"packed {size} bytes -> {len(out)} bytes")
    else:
        print(__doc__)
