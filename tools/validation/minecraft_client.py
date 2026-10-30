"""Minimal localhost-only Minecraft 1.20.1 (protocol 763) client for server regressions.

Packet IDs were read from the project's mapped ConnectionProtocol via --protocol-dump.
No renderer, account login, external servers or gameplay automation outside the disposable test server.
"""
import copy
import io
import socket
import struct
import threading
import time
import uuid
import zlib


def varint(value):
    value &= 0xFFFFFFFF
    out = bytearray()
    while True:
        byte = value & 127
        value >>= 7
        out.append(byte | (128 if value else 0))
        if not value:
            return bytes(out)


def read_varint(stream):
    value = 0
    for shift in range(0, 35, 7):
        raw = stream.read(1)
        if len(raw) != 1:
            raise EOFError("incomplete VarInt")
        value |= (raw[0] & 127) << shift
        if not raw[0] & 128:
            return value
    raise ValueError("VarInt exceeds five bytes")


def utf(value):
    data = value.encode("utf-8")
    return varint(len(data)) + data


def read_utf(stream):
    size = read_varint(stream)
    value = stream.read(size)
    if len(value) != size:
        raise EOFError("incomplete string")
    return value.decode("utf-8")


def read_nbt(data):
    stream = io.BytesIO(data)

    def number(kind):
        size = struct.calcsize(">" + kind)
        raw = stream.read(size)
        if len(raw) != size:
            raise EOFError("incomplete NBT value")
        return struct.unpack(">" + kind, raw)[0]

    def string():
        size = number("H")
        raw = stream.read(size)
        if len(raw) != size:
            raise EOFError("incomplete NBT string")
        return raw.decode("utf-8")

    def payload(kind, depth=0):
        if depth > 128:
            raise ValueError("test NBT depth exceeded")
        if kind in range(1, 7):
            return number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[kind])
        if kind == 7:
            return stream.read(number("i"))
        if kind == 8:
            return string()
        if kind == 9:
            child = number("b")
            size = number("i")
            if not 0 <= size <= 100000:
                raise ValueError("invalid test NBT list size")
            return [payload(child, depth + 1) for _ in range(size)]
        if kind == 10:
            result = {}
            while True:
                child = number("b")
                if child == 0:
                    return result
                name = string()
                result[name] = payload(child, depth + 1)
        if kind in (11, 12):
            size = number("i")
            if not 0 <= size <= 100000:
                raise ValueError("invalid test NBT array size")
            return [number("i" if kind == 11 else "q") for _ in range(size)]
        raise ValueError(f"unsupported NBT type {kind}")

    kind = number("b")
    if kind == 0:
        return None
    string()
    return payload(kind)


def apply_patch(snapshot, patch):
    result = copy.deepcopy(snapshot)
    for key in patch.get("Removed", []):
        result.pop(key, None)
    result.update(copy.deepcopy(patch.get("Values", {})))
    for key, nested in patch.get("Compounds", {}).items():
        result[key] = apply_patch(result.get(key, {}), nested)
    return result


def forge_login_reply(data):
    """FML3 login-wrapper interoperability, read from the locally installed Forge 47.4.8 codec.

    This protocol fixture acknowledges registry/config receipt; it does not load or render their content.
    """
    wrapper = io.BytesIO(data)
    target = read_utf(wrapper)
    size = read_varint(wrapper)
    payload = io.BytesIO(wrapper.read(size))
    if target != "fml:handshake":
        raise ValueError(f"unsupported Forge login target {target}")
    discriminator = payload.read(1)
    if discriminator == b"\x05":  # Mod metadata is informational; Forge marks it noResponse.
        return 5, None
    if discriminator == b"\x01":  # Mod list, channel versions, registry names, custom datapack registries.
        mods = [read_utf(payload) for _ in range(read_varint(payload))]
        channels = [(read_utf(payload), read_utf(payload)) for _ in range(read_varint(payload))]
        registries = [read_utf(payload) for _ in range(read_varint(payload))]
        datapacks = [read_utf(payload) for _ in range(read_varint(payload))]
        if datapacks:
            raise ValueError("test client does not implement custom datapack registries")
        reply = (b"\x02" + varint(len(mods)) + b"".join(utf(mod) for mod in mods)
                 + varint(len(channels)) + b"".join(utf(key) + utf(version) for key, version in channels)
                 + b"\x00")  # Known registry hashes: empty, as in Forge's default client reply.
    elif discriminator in (b"\x03", b"\x04"):
        reply = b"\x63"  # C2SAcknowledge, message discriminator 99; login index is the outer transaction id.
    else:
        raise ValueError(f"unsupported Forge handshake message {discriminator.hex()}")
    return discriminator[0], utf(target) + varint(len(reply)) + reply


class LocalClient:
    def __init__(self, port, name, loader="fabric", supports_delta=True):
        self.name = name
        self.loader = loader
        self.supports_delta = supports_delta
        self.profile_uuid = None
        self.knowledge = None
        self.full_packets = 0
        self.delta_packets = 0
        self.intro_packets = 0
        self.respawn_packets = 0
        self.dimension = None
        self.forge_messages = {}
        self.entities = {}  # Spawned entity UUID -> current protocol id, scoped to this connection.
        self.island_map = None
        self._use_sequence = 0
        self.error = None
        self._closing = False
        self._compression = -1
        self._play = False
        self._registered = False
        self._condition = threading.Condition()
        self._send_lock = threading.Lock()
        self._socket = socket.create_connection(("127.0.0.1", port), timeout=10)
        self._socket.settimeout(None)
        self._input = self._socket.makefile("rb")
        hostname = "localhost\x00FML3\x00" if loader == "forge" else "localhost"
        self.send(0, varint(763) + utf(hostname) + struct.pack(">H", port) + varint(2))
        self.send(0, utf(name) + b"\x00")  # LoginStart: no supplied UUID, offline server assigns one.
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def send(self, packet_id, payload=b""):
        with self._send_lock:
            body = varint(packet_id) + payload
            if self._compression >= 0:
                body = (varint(len(body)) + zlib.compress(body) if len(body) >= self._compression else b"\x00" + body)
            self._socket.sendall(varint(len(body)) + body)

    def _register(self):
        channels = ["terrassic:research_sync", "terrassic:intro", "terrassic:island_map", "terrassic:story", "terrassic:era_title"]
        if self.supports_delta:
            channels.append("terrassic:research_delta")
        physical = ["architectury:network", "fml:play", "fml:handshake", "fml:loginwrapper"] if self.loader == "forge" else []
        self.send(13, utf("minecraft:register") + b"\x00".join(channel.encode() for channel in channels + physical))
        self.send(13, utf("minecraft:brand") + utf("TerrassicRegression"))
        if self.loader == "forge":
            receivers = struct.pack(">i", len(channels)) + b"".join(utf(channel) for channel in channels)
            self.send(13, utf("architectury:network") + utf("architectury:sync_ids") + receivers)

    def _read_loop(self):
        try:
            while not self._closing:
                size = read_varint(self._input)
                if not 0 < size <= 8 * 1024 * 1024:
                    raise ValueError("invalid packet size")
                raw = self._input.read(size)
                if len(raw) != size:
                    raise EOFError("incomplete packet")
                if self._compression >= 0:
                    packet = io.BytesIO(raw)
                    unpacked = read_varint(packet)
                    raw = zlib.decompress(packet.read()) if unpacked else packet.read()
                    if unpacked and len(raw) != unpacked:
                        raise ValueError("compression length mismatch")
                packet = io.BytesIO(raw)
                packet_id = read_varint(packet)
                if not self._play:
                    if packet_id == 0:
                        raise RuntimeError("login rejected: " + read_utf(packet))
                    if packet_id == 1:
                        raise RuntimeError("test client requires the disposable offline-mode server")
                    if packet_id == 2:
                        self.profile_uuid = uuid.UUID(bytes=packet.read(16))
                        self._play = True
                    elif packet_id == 3:
                        self._compression = read_varint(packet)
                    elif packet_id == 4:
                        transaction = read_varint(packet)
                        channel = read_utf(packet)
                        if self.loader == "forge" and channel == "fml:loginwrapper":
                            kind, reply = forge_login_reply(packet.read())
                            self.forge_messages[kind] = self.forge_messages.get(kind, 0) + 1
                            if reply is not None:
                                self.send(2, varint(transaction) + b"\x01" + reply)
                        else:
                            self.send(2, varint(transaction) + b"\x00")
                    continue
                if packet_id == 1:  # AddEntity: protocol id followed by the entity UUID.
                    entity_id = read_varint(packet)
                    entity_uuid = str(uuid.UUID(bytes=packet.read(16)))
                    with self._condition:
                        self.entities[entity_uuid] = entity_id
                        self._condition.notify_all()
                elif packet_id == 40 and not self._registered:  # JoinGame: the server's play listener is now installed.
                    self._register()
                    self._registered = True
                elif packet_id == 35:  # KeepAlive
                    self.send(18, packet.read(8))
                elif packet_id == 60:  # PlayerPosition: x/y/z, yaw/pitch, relative flags, teleport id.
                    packet.read(33)
                    self.send(0, varint(read_varint(packet)))
                elif packet_id == 26:
                    raise RuntimeError("play disconnected: " + read_utf(packet))
                elif packet_id == 65:  # Respawn (also sent on dimension change): two resource keys first.
                    read_utf(packet)  # dimension type
                    with self._condition:
                        self.dimension = read_utf(packet)
                        self.respawn_packets += 1
                        self._condition.notify_all()
                elif packet_id == 23:
                    channel = read_utf(packet)
                    if channel == "architectury:network":
                        channel = read_utf(packet)
                    if channel == "terrassic:island_map":
                        size, extent, sea = (read_varint(packet) for _ in range(3))
                        if size != 128 or extent <= 0:
                            raise ValueError("unexpected island map dimensions")
                        arrays = []
                        for _ in range(2):
                            length = read_varint(packet)
                            if length != size * size:
                                raise ValueError("invalid island map array length")
                            data = packet.read(length)
                            if len(data) != length:
                                raise EOFError("incomplete island map array")
                            arrays.append(data)
                        with self._condition:
                            self.island_map = {"size": size, "extent": extent, "sea_level": sea,
                                               "heights": arrays[0], "kinds": arrays[1]}
                            self._condition.notify_all()
                    if channel in ("terrassic:research_sync", "terrassic:research_delta", "terrassic:intro"):
                        with self._condition:
                            if channel == "terrassic:intro":
                                self.intro_packets += 1
                            elif channel == "terrassic:research_sync":
                                self.knowledge = read_nbt(packet.read())
                                self.full_packets += 1
                            else:
                                if self.knowledge is None:
                                    raise RuntimeError("delta arrived before a full snapshot")
                                self.knowledge = apply_patch(self.knowledge, read_nbt(packet.read()))
                                self.delta_packets += 1
                            self._condition.notify_all()
        except (OSError, EOFError, ValueError, RuntimeError, zlib.error) as exc:
            if not self._closing:
                with self._condition:
                    self.error = str(exc)
                    self._condition.notify_all()

    def wait_for(self, predicate, timeout=15):
        deadline = time.monotonic() + timeout
        with self._condition:
            while not predicate(self):
                if self.error:
                    raise RuntimeError(f"{self.name}: {self.error}")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"{self.name}: expected network state not received")
                self._condition.wait(remaining)
            return copy.deepcopy(self.knowledge)

    def request_respawn(self):
        self.send(7, varint(0))  # ServerboundClientCommandPacket, PERFORM_RESPAWN.

    def interact_entity(self, entity_uuid, attack=False):
        entity_id = self.entities[str(entity_uuid)]
        action = varint(1) if attack else varint(0) + varint(0)  # ATTACK, or INTERACT with MAIN_HAND.
        self.send(16, varint(entity_id) + action + b"\x00")  # Not sneaking.

    def use_item(self):
        self._use_sequence += 1
        self.send(50, varint(0) + varint(self._use_sequence))  # MAIN_HAND and block-prediction sequence.

    def close(self):
        self._closing = True
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._socket.close()
        self._thread.join(timeout=2)
        self._input.close()
