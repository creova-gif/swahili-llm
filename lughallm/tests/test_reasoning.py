"""
Unit tests for LughaLLM System-2 Deep Reasoning Engine and Agentic Tool Registry.
"""

import unittest
from lughallm.src.reasoning.thinker import SwahiliReasoningEngine, reasoning_engine
from lughallm.src.agents.tools import ToolRegistry, tool_registry

try:
    from fastapi.testclient import TestClient
    from lughallm.src.api.main import app
    client = TestClient(app)
    HAS_FASTAPI = True
except ImportError:
    client = None
    HAS_FASTAPI = False


class TestSwahiliReasoningEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SwahiliReasoningEngine()

    def test_generate_reasoning_trace_tags(self):
        trace = self.engine.generate_reasoning_trace(
            prompt="Nataka kuhesabu kodi ya TRA",
            dialect="kiswahili_sanifu",
            domain="fedha_na_uchumi"
        )
        self.assertTrue(trace.startswith("<fikiri>"))
        self.assertTrue(trace.endswith("</fikiri>"))
        self.assertIn("kiswahili_sanifu", trace)
        self.assertIn("fedha_na_uchumi", trace)
        self.assertIn("HALLUCINATION CHECK", trace)

    def test_process_with_reasoning_toggle(self):
        base_resp = "Hapa kuna muongozo wa kodi."
        # When include_thinking=False
        resp_plain = self.engine.process_with_reasoning(
            prompt="Kodi", dialect="kiswahili_sanifu", domain="fedha",
            base_response=base_resp, include_thinking=False
        )
        self.assertEqual(resp_plain, base_resp)
        self.assertNotIn("<fikiri>", resp_plain)

        # When include_thinking=True
        resp_reasoned = self.engine.process_with_reasoning(
            prompt="Kodi", dialect="kiswahili_sanifu", domain="fedha",
            base_response=base_resp, include_thinking=True
        )
        self.assertIn("<fikiri>", resp_reasoned)
        self.assertIn("</fikiri>", resp_reasoned)
        self.assertTrue(resp_reasoned.endswith(base_resp))

    def test_apply_eloquent_style(self):
        robotic = "Kwa ujumla, tunaweza kusema kwamba kilimo cha umwagiliaji kinaleta faida kubwa."
        clean = self.engine.apply_eloquent_style(robotic, "kiswahili_sanifu")
        self.assertFalse(clean.startswith("Kwa ujumla, tunaweza kusema kwamba"))
        self.assertTrue(clean.startswith("kilimo cha umwagiliaji"))

    def test_adabu_and_politeness(self):
        # 1. Elder greeting Shikamoo -> Marahaba
        resp = self.engine.apply_adabu_and_politeness("Karibu.", "Shikamoo mwalimu.", "kiswahili_sanifu")
        self.assertTrue(resp.startswith("Marahaba."))

        # 2. Empathy greeting
        resp_pole = self.engine.apply_adabu_and_politeness("Tunaendelea vizuri.", "Habari za kazi na pole na kazi.", "kiswahili_sanifu")
        self.assertTrue(resp_pole.startswith("Asante sana"))

        # 3. Indirect demurral for blunt refusals
        resp_demurral = self.engine.apply_adabu_and_politeness("Hapana. Huwezi kufanya hivyo.", "Naomba msaada", "kiswahili_sanifu")
        self.assertNotIn("Hapana.", resp_demurral)
        self.assertIn("ugumu", resp_demurral)


class TestAgenticToolRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = tool_registry

    def test_default_tools_registered(self):
        definitions = self.registry.get_tool_definitions()
        tool_names = [t["function"]["name"] for t in definitions]
        self.assertIn("pata_bei_za_soko", tool_names)
        self.assertIn("hali_ya_hewa_kilimo", tool_names)
        self.assertIn("hesabu_kodi_kikanda", tool_names)

    def test_market_prices_tool(self):
        res = self.registry.execute_tool(
            "pata_bei_za_soko",
            {"zao": "mahindi", "mji": "Nairobi"}
        )
        self.assertEqual(res["hali"], "sahihi")
        self.assertIn("KES", res["bei_ya_sasa"])

    def test_weather_tool(self):
        res = self.registry.execute_tool(
            "hali_ya_hewa_kilimo",
            {"eneo": "Morogoro"}
        )
        self.assertEqual(res["eneo"], "Morogoro")
        self.assertIn("Mvua", res["hali_ya_hewa"])

    def test_tax_calculator_tool(self):
        # Tanzania TRA VAT is 18%
        res_tz = self.registry.execute_tool(
            "hesabu_kodi_kikanda",
            {"kiasi": 100000, "nchi": "Tanzania"}
        )
        self.assertEqual(res_tz["kiwango_cha_vat"], "18%")
        self.assertEqual(res_tz["makisio_ya_vat"], 18000.0)
        self.assertEqual(res_tz["jumla_pamoja_na_vat"], 118000.0)

        # Kenya KRA VAT is 16%
        res_ke = self.registry.execute_tool(
            "hesabu_kodi_kikanda",
            {"kiasi": 100000, "nchi": "Kenya"}
        )
        self.assertEqual(res_ke["kiwango_cha_vat"], "16%")
        self.assertEqual(res_ke["makisio_ya_vat"], 16000.0)

    def test_unregistered_tool(self):
        res = self.registry.execute_tool("chombo_kisichopo", {})
        self.assertIn("error", res)

    def test_loan_simplifier_tool(self):
        # 50k principal, 65k return in 14 days (30% in 14 days = ~782% APR - predatory loan)
        res = self.registry.execute_tool(
            "rahisisha_mkopo_kidijitali",
            {"kiasi_cha_mkopo": 50000, "kiasi_cha_kurejesha": 65000, "muda_siku": 14}
        )
        self.assertEqual(res["riba_pesa"], 15000)
        self.assertIn("782", res["riba_ya_mwaka_apr"])
        self.assertIn("Hatari", res["tathmini_ya_hatari"])
        self.assertIn("VICOBA", res["ushauri_wa_kifedha"])

    def test_crop_disease_tool(self):
        res = self.registry.execute_tool(
            "tiba_ya_magonjwa_ya_mimea",
            {"zao": "mahindi", "dalili_au_mdudu": "funza wa mahindi"}
        )
        self.assertIn("Spodoptera frugiperda", res["utambuzi"])
        self.assertIn("majivu", res["tiba_na_kinga"])


@unittest.skipUnless(HAS_FASTAPI, "FastAPI / TestClient dependencies not installed.")
class TestReasoningAndToolsAPI(unittest.TestCase):

    def test_sovereign_status_endpoint(self):
        res = client.get("/v1/sovereign/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "air_gapped_compliant")
        self.assertTrue(data["cloud_leakage_prevented"])
        self.assertEqual(data["telemetry_egress"], "blocked_by_design")

    def test_list_tools_endpoint(self):
        res = client.get("/v1/tools")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tools", data)
        names = [t["function"]["name"] for t in data["tools"]]
        self.assertIn("pata_bei_za_soko", names)

    def test_execute_tool_endpoint(self):
        payload = {
            "name": "hesabu_kodi_kikanda",
            "arguments": {"kiasi": 50000, "nchi": "Kenya"}
        }
        res = client.post("/v1/tools/execute", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["result"]["kiwango_cha_vat"], "16%")

    def test_chat_completions_with_thinking(self):
        payload = {
            "model": "lughallm-llama3-8b",
            "messages": [
                {"role": "user", "content": "Habari za asubuhi."}
            ],
            "include_thinking": True
        }
        res = client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        self.assertIn("<fikiri>", content)
        self.assertIn("</fikiri>", content)


if __name__ == "__main__":
    unittest.main()
