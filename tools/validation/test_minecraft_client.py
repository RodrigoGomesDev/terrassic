"""Conformance fixtures for the localhost protocol client's binary boundaries."""
import copy
import io
import unittest

from minecraft_client import apply_patch, forge_login_reply, read_nbt, read_utf, read_varint, utf, varint


class ProtocolFixtures(unittest.TestCase):
    def test_known_varint_vectors(self):
        for number, encoded in [(0, b"\x00"), (127, b"\x7f"), (128, b"\x80\x01"),
                                (300, b"\xac\x02"), (2147483647, b"\xff\xff\xff\xff\x07")]:
            self.assertEqual(varint(number), encoded)
            self.assertEqual(read_varint(io.BytesIO(encoded)), number)

    def test_strings_use_byte_length(self):
        self.assertEqual(utf("Ámbar"), b"\x06\xc3\x81mbar")
        self.assertEqual(read_utf(io.BytesIO(b"\x06\xc3\x81mbar")), "Ámbar")

    def test_known_nbt_compound_and_list(self):
        # Unnamed root compound: int N=42, string S=abc, then end.
        encoded = bytes.fromhex("0a0000 0300014e0000002a 080001530003616263 00")
        self.assertEqual(read_nbt(encoded), {"N": 42, "S": "abc"})
        # Unnamed root compound: list L contains two strings a,b.
        encoded = bytes.fromhex("0a0000 0900014c0800000002000161000162 00")
        self.assertEqual(read_nbt(encoded), {"L": ["a", "b"]})
        self.assertIsNone(read_nbt(b"\x00"))

    def test_incomplete_values_are_rejected(self):
        with self.assertRaises(EOFError):
            read_varint(io.BytesIO(b"\x80"))
        with self.assertRaises(ValueError):
            read_varint(io.BytesIO(b"\x80" * 5))
        with self.assertRaises(EOFError):
            read_utf(io.BytesIO(b"\x03ab"))
        with self.assertRaises(EOFError):
            read_nbt(b"\x0a\x00")

    def test_nested_patch_and_input_independence(self):
        before = {"Species": {"rex": {"Level": 2, "Old": 1}}, "Pages": ["a"], "OldFlag": True}
        backup = copy.deepcopy(before)
        patch = {"Values": {"Pages": ["a", "b"]}, "Removed": ["OldFlag"], "Compounds": {
            "Species": {"Compounds": {"rex": {"Values": {"Level": 3}, "Removed": ["Old"]}}}}}
        after = apply_patch(before, patch)
        self.assertEqual(after, {"Species": {"rex": {"Level": 3}}, "Pages": ["a", "b"]})
        self.assertEqual(before, backup)
        after["Pages"].append("c")
        self.assertEqual(patch["Values"]["Pages"], ["a", "b"])

    def test_forge_login_wrapper(self):
        mod_list = (b"\x01" + varint(1) + utf("terrassic") + varint(1)
                    + utf("architectury:network") + utf("1") + varint(1) + utf("minecraft:block") + b"\x00")
        kind, reply = forge_login_reply(utf("fml:handshake") + varint(len(mod_list)) + mod_list)
        self.assertEqual(kind, 1)
        wrapper = io.BytesIO(reply)
        self.assertEqual(read_utf(wrapper), "fml:handshake")
        nested = wrapper.read(read_varint(wrapper))
        self.assertEqual(nested, b"\x02\x01" + utf("terrassic") + b"\x01" + utf("architectury:network") + utf("1") + b"\x00")
        kind, reply = forge_login_reply(utf("fml:handshake") + b"\x01\x03")
        self.assertEqual((kind, reply), (3, utf("fml:handshake") + b"\x01\x63"))
        self.assertEqual(forge_login_reply(utf("fml:handshake") + b"\x01\x05"), (5, None))


if __name__ == "__main__":
    unittest.main()
