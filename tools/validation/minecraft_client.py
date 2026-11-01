"""Minimal localhost-only Minecraft 1.21.1 (protocol 767) client for server regressions, Fabric only.

Packet IDs come from the vanilla data generator (server.jar --reports, reports/packets.json). A NeoForge server
negotiates its payload channels with its own client, which this client does not implement.
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
    return payload(kind)  # network NBT: the root has no name since 1.20.2


def apply_patch(snapshot, patch):
    result = copy.deepcopy(snapshot)
    for key in patch.get("Removed", []):
        result.pop(key, None)
    result.update(copy.deepcopy(patch.get("Values", {})))
    for key, nested in patch.get("Compounds", {}).items():
        result[key] = apply_patch(result.get(key, {}), nested)
    return result


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
        self.entities = {}  # Spawned entity UUID -> current protocol id, scoped to this connection.
        self.island_map = None
        self._use_sequence = 0
        self.error = None
        self._closing = False
        self._compression = -1
        self._phase = "login"
        self._registered = False
        self._condition = threading.Condition()
        self._send_lock = threading.Lock()
        self._socket = socket.create_connection(("127.0.0.1", port), timeout=10)
        self._socket.settimeout(None)
        self._input = self._socket.makefile("rb")
        if loader != "fabric":
            raise ValueError("the protocol client only speaks to Fabric servers since 1.21.1")
        hostname = "localhost"
        self.send(0, varint(767) + utf(hostname) + struct.pack(">H", port) + varint(2))
        self.send(0, utf(name) + uuid.uuid3(uuid.NAMESPACE_DNS, "OfflinePlayer:" + name).bytes)  # LoginStart: the UUID is required.
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
        self.send(18, utf("minecraft:register") + b"\x00".join(channel.encode() for channel in channels))
        self.send(18, utf("minecraft:brand") + utf("TerrassicRegression"))

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
                if self._phase == "login":
                    if packet_id == 0:
                        raise RuntimeError("login rejected: " + read_utf(packet))
                    if packet_id == 1:
                        raise RuntimeError("test client requires the disposable offline-mode server")
                    if packet_id == 2:
                        self.profile_uuid = uuid.UUID(bytes=packet.read(16))
                        self.send(3)  # LoginAcknowledged: from here on, the configuration phase.
                        self._phase = "configuration"
                    elif packet_id == 3:
                        self._compression = read_varint(packet)
                    elif packet_id == 4:
                        self.send(2, varint(read_varint(packet)) + b"\x00")
                    continue
                if self._phase == "configuration":
                    if packet_id == 2:
                        raise RuntimeError("configuration disconnected")
                    if packet_id == 3:  # FinishConfiguration
                        self.send(3)
                        self._phase = "play"
                    elif packet_id == 4:  # KeepAlive
                        self.send(4, packet.read(8))
                    elif packet_id == 5:  # Ping
                        self.send(5, packet.read(4))
                    elif packet_id == 14:  # SelectKnownPacks: none, so the registries come in full.
                        self.send(7, varint(0))
                    continue
                if packet_id == 1:  # AddEntity: protocol id followed by the entity UUID.
                    entity_id = read_varint(packet)
                    entity_uuid = str(uuid.UUID(bytes=packet.read(16)))
                    with self._condition:
                        self.entities[entity_uuid] = entity_id
                        self._condition.notify_all()
                elif packet_id == 43 and not self._registered:  # JoinGame: the server's play listener is now installed.
                    self._register()
                    self._registered = True
                elif packet_id == 38:  # KeepAlive
                    self.send(24, packet.read(8))
                elif packet_id == 53:  # Ping
                    self.send(39, packet.read(4))
                elif packet_id == 12:  # ChunkBatchFinished: keeps the server sending chunks.
                    self.send(8, struct.pack(">f", 20.0))
                elif packet_id == 64:  # PlayerPosition: x/y/z, yaw/pitch, relative flags, teleport id.
                    packet.read(33)
                    self.send(0, varint(read_varint(packet)))
                elif packet_id == 29:
                    raise RuntimeError("play disconnected: " + repr(read_nbt(packet.read())))
                elif packet_id == 71:  # Respawn (also sent on dimension change): dimension type id, then its key.
                    read_varint(packet)
                    with self._condition:
                        self.dimension = read_utf(packet)
                        self.respawn_packets += 1
                        self._condition.notify_all()
                elif packet_id == 25:
                    channel = read_utf(packet)
                    for _ in range(2):  # Architectury frames its bytes twice: payload and buffer, each with a length.
                        packet = io.BytesIO(packet.read(read_varint(packet)))
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
        self.send(9, varint(0))  # ServerboundClientCommandPacket, PERFORM_RESPAWN.

    def interact_entity(self, entity_uuid, attack=False):
        entity_id = self.entities[str(entity_uuid)]
        action = varint(1) if attack else varint(0) + varint(0)  # ATTACK, or INTERACT with MAIN_HAND.
        self.send(22, varint(entity_id) + action + b"\x00")  # Not sneaking.

    def use_item(self):
        self._use_sequence += 1
        self.send(57, varint(0) + varint(self._use_sequence) + struct.pack(">ff", 0.0, 0.0))  # MAIN_HAND, sequence, yaw, pitch.

    def release_item(self):
        self.send(36, varint(5) + b"\x00" * 8 + b"\x00" + varint(0))  # PlayerAction RELEASE_USE_ITEM.

    def close(self):
        self._closing = True
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._socket.close()
        self._thread.join(timeout=2)
        self._input.close()
