"""
Unit tests for LughaClient SDK.
"""

import unittest
from lughallm.client import LughaClient, LughaError


class TestLughaClient(unittest.TestCase):

    def setUp(self):
        self.client = LughaClient(api_key="lug_live_testkey123", base_url="http://localhost:8000")

    def test_client_init(self):
        self.assertEqual(self.client.api_key, "lug_live_testkey123")
        self.assertEqual(self.client.base_url, "http://localhost:8000")

    def test_client_connection_error_handling(self):
        # Client targeting non-existent port raises cleanly wrapped LughaError
        bad_client = LughaClient(api_key="test", base_url="http://127.0.0.1:59999")
        with self.assertRaises(LughaError):
            bad_client.check_balance()


if __name__ == "__main__":
    unittest.main()
