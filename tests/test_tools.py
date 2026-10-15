import os
import tempfile
import unittest

from tools import load


class TestTools(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def path(self, name):
        return os.path.join(self.folder.name, name)

    def test_white_list(self):
        white = load("white-list")
        p = self.path("white.json")
        white.add("10.0.0.1", p)
        white.add("10.0.0.1", p)  # repetida, no se duplica
        self.assertEqual(white.get_all(p), ["10.0.0.1"])
        self.assertTrue(white.contains("10.0.0.1", p))
        white.remove("10.0.0.1", p)
        self.assertFalse(white.contains("10.0.0.1", p))

    def test_black_list(self):
        black = load("black-list")
        p = self.path("black.json")
        black.add("6.6.6.6", p)
        self.assertTrue(black.contains("6.6.6.6", p))

    def test_keys(self):
        keys = load("keys")
        p = self.path("keys.json")
        key = keys.generate_key()
        keys.save_key("admin", key, p)
        self.assertTrue(keys.verify_key("admin", key, p))
        self.assertFalse(keys.verify_key("admin", "otra-clave", p))

    def test_users(self):
        users = load("users")
        p = self.path("users.json")
        users.add_user("ana", "admin", p)
        self.assertEqual(users.find_user("ana", p), {"role": "admin"})
        self.assertIsNone(users.find_user("luis", p))

    def test_enterprises(self):
        enterprises = load("enterprises")
        p = self.path("enterprises.json")
        enterprises.add_enterprise("ACME", p)
        self.assertEqual(enterprises.get_enterprises(p), ["ACME"])


if __name__ == "__main__":
    unittest.main()