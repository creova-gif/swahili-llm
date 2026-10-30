"""
Integration tests for LughaLLM FastAPI endpoints.
Gracefully skips if dependencies are not yet installed in the active environment.
"""

import unittest

try:
    from fastapi.testclient import TestClient
    from lughallm.src.api.main import app
    client = TestClient(app)
    HAS_FASTAPI = True
except ImportError:
    client = None
    HAS_FASTAPI = False


@unittest.skipUnless(HAS_FASTAPI, "FastAPI / TestClient dependencies not installed.")
class TestAPI(unittest.TestCase):

    def test_health_endpoint(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("kiswahili_sanifu", data["supported_dialects"])

    def test_list_models_endpoint(self):
        res = client.get("/v1/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        model_ids = [m["id"] for m in data["data"]]
        self.assertIn("lughallm-llama3-8b", model_ids)

    def test_chat_completions_endpoint(self):
        payload = {
            "model": "lughallm-llama3-8b",
            "messages": [
                {"role": "user", "content": "Manze niko na swali kuhusu mbogi na ganji."}
            ]
        }
        res = client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["model"], "lughallm-llama3-8b")
        self.assertGreater(len(data["choices"]), 0)
        self.assertEqual(data["detected_dialect"], "sheng_nairobi")
        self.assertGreater(data["usage"]["total_tokens"], 0)

    def test_whatsapp_webhook_endpoint(self):
        payload = {
            "phone_number": "+255754112233",
            "message": "Habari, naomba kujua kuhusu mbolea na kupalilia mahindi.",
            "user_name": "Juma"
        }
        res = client.post("/v1/webhooks/whatsapp", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Kilimo Agent", data["reply"])

    def test_mpesa_simulate_endpoint(self):
        payload = {
            "phone_number": "255712345678",
            "amount_tzs": 5000.0,
            "account_reference": "LUGHA-TOKENS"
        }
        res = client.post("/v1/payments/mpesa/simulate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "COMPLETED")
        self.assertEqual(data["tokens_credited"], 200000)

    def test_chat_completions_empty_message_rejected(self):
        payload = {
            "model": "lughallm-llama3-8b",
            "messages": [
                {"role": "user", "content": "   "}
            ]
        }
        res = client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("non-empty", data["detail"])

    def test_mpesa_negative_amount_rejected(self):
        payload = {
            "phone_number": "255712345678",
            "amount_tzs": -100.0,
            "account_reference": "LUGHA-TOKENS"
        }
        res = client.post("/v1/payments/mpesa/simulate", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("greater than zero", data["detail"])

    def test_threads_api_lifecycle(self):
        # 1. Create thread
        res = client.post("/v1/threads", json={"title": "Kilimo cha Maharage", "user_id": "test_user_42"})
        self.assertEqual(res.status_code, 200)
        thread = res.json()
        self.assertIn("thread_id", thread)
        t_id = thread["thread_id"]

        # 2. Send multi-turn message
        msg_res = client.post(f"/v1/threads/{t_id}/messages", json={
            "content": "Habari, nataka kujua magonjwa ya maharage",
            "include_thinking": True
        })
        self.assertEqual(msg_res.status_code, 200)
        msg_data = msg_res.json()
        self.assertIn("message", msg_data)
        self.assertEqual(msg_data["message"]["role"], "assistant")
        self.assertIsNotNone(msg_data["message"]["reasoning_trace"])

        # 3. Retrieve thread messages
        hist_res = client.get(f"/v1/threads/{t_id}/messages")
        self.assertEqual(hist_res.status_code, 200)
        hist = hist_res.json()
        self.assertEqual(len(hist["messages"]), 2)
        self.assertEqual(hist["messages"][0]["role"], "user")
        self.assertEqual(hist["messages"][1]["role"], "assistant")

    def test_chat_completions_streaming(self):
        payload = {
            "model": "lughallm-llama3-8b",
            "messages": [{"role": "user", "content": "Habari za mchana"}],
            "stream": True
        }
        res = client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))
        self.assertIn("data: ", res.text)
        self.assertIn("[DONE]", res.text)


if __name__ == "__main__":
    unittest.main()
