import unittest
from app import add_item

class ReadingListTests(unittest.TestCase):
    def test_accepts_web_url_and_trims_space(self):
        self.assertEqual(add_item([], " https://example.com/a "), ["https://example.com/a"])

    def test_rejects_invalid_scheme_missing_host_and_credentials(self):
        for value in ("", "javascript:alert(1)", "https://", "https://name:pass@example.com",
                      "https://bad host/", "https://example.com:abc/", "https://example.com:99999/",
                      "https://exam\nple.com/", "https://@example.com/"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                add_item([], value)

    def test_duplicate_add_is_idempotent(self):
        items = []
        add_item(items, "https://example.com")
        add_item(items, "https://example.com")
        self.assertEqual(items, ["https://example.com"])

if __name__ == "__main__":
    unittest.main()
