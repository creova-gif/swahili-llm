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

    def test_multi_turn_thread_and_messages(self):
        thread = self.db.create_thread(title="Kilimo cha Mahindi", user_id="user_tz_01", dialect="kiswahili_sanifu")
        self.assertTrue(thread["thread_id"].startswith("th_"))
        self.assertEqual(thread["title"], "Kilimo cha Mahindi")

        # Add user message
        m1 = self.db.add_chat_message(
            thread_id=thread["thread_id"],
            role="user",
            content="Habari, nina shamba Morogoro, nianze na mbolea gani?",
            tokens=24
        )
        self.assertTrue(m1["message_id"].startswith("msg_"))

        # Add assistant message with reasoning trace
        m2 = self.db.add_chat_message(
            thread_id=thread["thread_id"],
            role="assistant",
            content="Marahaba! Kwa Morogoro, anza na mbolea ya kupandia kama DAP au Minjingu.",
            reasoning_trace="<fikiri>1. Morogoro ni ukanda wa mashariki...</fikiri>",
            tokens=32
        )

        # Retrieve messages
        messages = self.db.get_thread_messages(thread["thread_id"])
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertIn("Minjingu", messages[1]["content"])

        # List user threads
        threads = self.db.list_threads("user_tz_01")
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["thread_id"], thread["thread_id"])


if __name__ == "__main__":
    unittest.main()
