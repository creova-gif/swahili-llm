"""
SQLite-based Token Ledger and API Key Storage for LughaLLM.
Standard-library only, fully transactional, and zero-dependency.
"""

import sqlite3
import os
import uuid
import time
from typing import Optional, Dict, Any, List


class TokenLedgerDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "lughallm_ledger.sqlite3")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # API Keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    api_key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    balance_tokens INTEGER NOT NULL DEFAULT 50000,
                    created_at INTEGER NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1
                )
            """)
            # M-Pesa & Mobile Money Transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    checkout_id TEXT PRIMARY KEY,
                    api_key TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    amount_tzs REAL NOT NULL,
                    tokens_credited INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)
            # Usage Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    request_id TEXT PRIMARY KEY,
                    api_key TEXT NOT NULL,
                    tokens_consumed INTEGER NOT NULL,
                    cost_tzs REAL NOT NULL,
                    dialect TEXT,
                    domain TEXT,
                    timestamp INTEGER NOT NULL
                )
            """)
            # Chatbot Multi-Turn Conversation Threads
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_threads (
                    thread_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    dialect TEXT NOT NULL DEFAULT 'auto',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
            """)
            # Chatbot Messages History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    reasoning_trace TEXT,
                    tokens INTEGER NOT NULL DEFAULT 0,
                    timestamp INTEGER NOT NULL,
                    FOREIGN KEY (thread_id) REFERENCES chat_threads(thread_id)
                )
            """)
            conn.commit()

            # Seed default demo key if none exists
            cursor.execute("SELECT COUNT(*) as count FROM api_keys")
            row = cursor.fetchone()
            if row["count"] == 0:
                self.create_api_key(key="lug_live_demo12345", name="Default Demo Account", initial_tokens=100000)

    def create_api_key(self, name: str, key: Optional[str] = None, initial_tokens: int = 50000) -> str:
        if key is None:
            key = f"lug_live_{uuid.uuid4().hex[:16]}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO api_keys (api_key, name, balance_tokens, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (key, name, initial_tokens, int(time.time())))
            conn.commit()
        return key

    def get_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM api_keys WHERE api_key = ?", (api_key,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def credit_tokens(self, api_key: str, tokens: int, checkout_id: str, phone: str, amount_tzs: float) -> int:
        """Credits tokens to an API key and logs the M-Pesa transaction atomically."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_keys 
                SET balance_tokens = balance_tokens + ? 
                WHERE api_key = ?
            """, (tokens, api_key))
            
            cursor.execute("""
                INSERT INTO payment_transactions 
                (checkout_id, api_key, phone_number, amount_tzs, tokens_credited, status, timestamp)
                VALUES (?, ?, ?, ?, ?, 'COMPLETED', ?)
            """, (checkout_id, api_key, phone, amount_tzs, tokens, int(time.time())))
            conn.commit()

            cursor.execute("SELECT balance_tokens FROM api_keys WHERE api_key = ?", (api_key,))
            res = cursor.fetchone()
            return res["balance_tokens"] if res else 0

    def debit_tokens(self, api_key: str, tokens: int, request_id: str, cost_tzs: float, dialect: str, domain: str) -> bool:
        """Debits tokens if sufficient balance exists. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance_tokens, is_active FROM api_keys WHERE api_key = ?", (api_key,))
            row = cursor.fetchone()
            if not row or row["is_active"] != 1 or row["balance_tokens"] < tokens:
                return False

            cursor.execute("""
                UPDATE api_keys 
                SET balance_tokens = balance_tokens - ? 
                WHERE api_key = ?
            """, (tokens, api_key))

            cursor.execute("""
                INSERT INTO usage_logs 
                (request_id, api_key, tokens_consumed, cost_tzs, dialect, domain, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (request_id, api_key, tokens, cost_tzs, dialect, domain, int(time.time())))
            conn.commit()
            return True

    def create_thread(self, title: str, user_id: str = "guest", dialect: str = "auto") -> Dict[str, Any]:
        """Creates a new multi-turn conversation thread."""
        thread_id = f"th_{uuid.uuid4().hex[:12]}"
        now = int(time.time())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_threads (thread_id, user_id, title, dialect, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (thread_id, user_id, title, dialect, now, now))
            conn.commit()
        return {
            "thread_id": thread_id,
            "user_id": user_id,
            "title": title,
            "dialect": dialect,
            "created_at": now,
            "updated_at": now
        }

    def list_threads(self, user_id: str = "guest", limit: int = 20) -> List[Dict[str, Any]]:
        """Lists recent conversation threads for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_threads 
                WHERE user_id = ? 
                ORDER BY updated_at DESC LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def add_chat_message(self, thread_id: str, role: str, content: str, reasoning_trace: Optional[str] = None, tokens: int = 0) -> Dict[str, Any]:
        """Appends a message to a conversation thread and updates thread timestamp."""
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = int(time.time())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (message_id, thread_id, role, content, reasoning_trace, tokens, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, thread_id, role, content, reasoning_trace, tokens, now))
            cursor.execute("""
                UPDATE chat_threads SET updated_at = ? WHERE thread_id = ?
            """, (now, thread_id))
            conn.commit()
        return {
            "message_id": msg_id,
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "reasoning_trace": reasoning_trace,
            "tokens": tokens,
            "timestamp": now
        }

    def get_thread_messages(self, thread_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves messages for a conversation thread in chronological order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE thread_id = ? 
                ORDER BY timestamp ASC LIMIT ?
            """, (thread_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]


# Global default instance
ledger = TokenLedgerDB()
