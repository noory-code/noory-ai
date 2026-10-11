import unittest

from app.errors import ConfigError
from app.host import parse_host


class ParseHostTest(unittest.TestCase):
    def test_valid_host_returned_unchanged(self):
        self.assertEqual(parse_host("example.com"), "example.com")

    def test_invalid_hosts_raise_config_error(self):
        for value in ["bad", "", "exa mple.com", "example.com\n", "\t.", None, 123]:
            with self.subTest(value=value):
                with self.assertRaises(ConfigError):
                    parse_host(value)


if __name__ == "__main__":
    unittest.main()
