"""
Unit tests for SQLite TokenLedgerDB.
"""

import unittest
import os
import tempfile
from lughallm.src.db.storage import TokenLedgerDB


class TestTokenLedger(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
        self.temp_file.close()
        self.db = TokenLedgerDB(db_path=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_create_and_get_key(self):
        key = self.db.create_api_key(name="Test Suite App", initial_tokens=60000)
        self.assertTrue(key.startswith("lug_live_"))
        info = self.db.get_key_info(key)
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "Test Suite App")
        self.assertEqual(info["balance_tokens"], 60000)

    def test_credit_and_debit_flow(self):
        key = self.db.create_api_key(name="Billing Test", initial_tokens=1000)
        
        # Debit successful
        success = self.db.debit_tokens(
            api_key=key,
            tokens=400,
            request_id="req_001",
            cost_tzs=10.0,
            dialect="sheng",
            domain="cultural"
        )
        self.assertTrue(success)
        info = self.db.get_key_info(key)
        self.assertEqual(info["balance_tokens"], 600)

        # Debit fails if insufficient
        fail = self.db.debit_tokens(
            api_key=key,
            tokens=700,
            request_id="req_002",
            cost_tzs=17.5,
            dialect="sheng",
            domain="cultural"
        )
        self.assertFalse(fail)

        # Credit via M-Pesa
        new_bal = self.db.credit_tokens(
            api_key=key,
            tokens=2000,
            checkout_id="tx_12345",
            phone="255712345678",
            amount_tzs=50.0
        )
        self.assertEqual(new_bal, 2600)


if __name__ == "__main__":
    unittest.main()
