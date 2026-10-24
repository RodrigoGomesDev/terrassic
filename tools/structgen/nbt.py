"""Minimal NBT writer for structure templates (big-endian, gzipped), no dependencies.

Values: dict -> compound, str -> string, bool -> byte, Int/Byte/Short/Long/Float/Double wrappers or plain int
(int -> TAG_Int) / float (-> TAG_Double), list -> list (element type from the first element), IntArray -> int array.
"""
import gzip
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY = range(12)


class Byte(int):
    pass


class Short(int):
    pass


class Long(int):
    pass


class Float(float):
    pass


class IntArray(list):
    pass


def tag_type(v):
    if isinstance(v, bool) or isinstance(v, Byte):
        return BYTE
    if isinstance(v, Short):
        return SHORT
    if isinstance(v, Long):
        return LONG
    if isinstance(v, int):
        return INT
    if isinstance(v, Float):
        return FLOAT
    if isinstance(v, float):
        return DOUBLE
    if isinstance(v, str):
        return STRING
    if isinstance(v, IntArray):
        return INT_ARRAY
    if isinstance(v, list):
        return LIST
    if isinstance(v, dict):
        return COMPOUND
    raise TypeError(f"no NBT type for {type(v)}")


def _string(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def payload(v):
    t = tag_type(v)
    if t == BYTE:
        return struct.pack(">b", int(v))
    if t == SHORT:
        return struct.pack(">h", v)
    if t == INT:
        return struct.pack(">i", v)
    if t == LONG:
        return struct.pack(">q", v)
    if t == FLOAT:
        return struct.pack(">f", v)
    if t == DOUBLE:
        return struct.pack(">d", v)
    if t == STRING:
        return _string(v)
    if t == INT_ARRAY:
        return struct.pack(">i", len(v)) + b"".join(struct.pack(">i", x) for x in v)
    if t == LIST:
        et = tag_type(v[0]) if v else END
        for x in v:
            if tag_type(x) != et:
                raise TypeError("NBT lists must hold one type")
        return struct.pack(">bi", et, len(v)) + b"".join(payload(x) for x in v)
    out = b""
    for k, x in v.items():
        out += struct.pack(">b", tag_type(x)) + _string(k) + payload(x)
    return out + struct.pack(">b", END)


def write(path, root):
    """Root compound with an empty name, gzipped (the format of .nbt structure files)."""
    data = struct.pack(">b", COMPOUND) + _string("") + payload(root)
    with gzip.GzipFile(path, "wb", mtime=0) as f:  # mtime 0: same bytes every run, quiet git diffs
        f.write(data)


# -- reader, for the round-trip check -------------------------------------------------------------------------

def _read(buf, pos, t):
    if t == BYTE:
        return struct.unpack_from(">b", buf, pos)[0], pos + 1
    if t == SHORT:
        return struct.unpack_from(">h", buf, pos)[0], pos + 2
    if t == INT:
        return struct.unpack_from(">i", buf, pos)[0], pos + 4
    if t == LONG:
        return struct.unpack_from(">q", buf, pos)[0], pos + 8
    if t == FLOAT:
        return struct.unpack_from(">f", buf, pos)[0], pos + 4
    if t == DOUBLE:
        return struct.unpack_from(">d", buf, pos)[0], pos + 8
    if t == STRING:
        n = struct.unpack_from(">H", buf, pos)[0]
        return buf[pos + 2:pos + 2 + n].decode("utf-8"), pos + 2 + n
    if t == INT_ARRAY:
        n = struct.unpack_from(">i", buf, pos)[0]
        return list(struct.unpack_from(f">{n}i", buf, pos + 4)), pos + 4 + 4 * n
    if t == LIST:
        et, n = struct.unpack_from(">bi", buf, pos)
        pos += 5
        out = []
        for _ in range(n):
            x, pos = _read(buf, pos, et)
            out.append(x)
        return out, pos
    if t == COMPOUND:
        out = {}
        while True:
            tt = buf[pos]
            pos += 1
            if tt == END:
                return out, pos
            name, pos = _read(buf, pos, STRING)
            out[name], pos = _read(buf, pos, tt)
    raise ValueError(f"tag {t}")


def read(path):
    with gzip.open(path, "rb") as f:
        buf = f.read()
    assert buf[0] == COMPOUND
    _name, pos = _read(buf, 1, STRING)
    root, _ = _read(buf, pos, COMPOUND)
    return root
