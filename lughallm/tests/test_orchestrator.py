"""
Unit tests for Dialect Detection and Multi-Agent Orchestrator.
Compatible with standard library unittest and pytest.
"""

import unittest
from lughallm.src.orchestrator.agent import DialectDetector, LughaOrchestrator


class TestOrchestrator(unittest.TestCase):

    def test_dialect_detector_sheng(self):
        detector = DialectDetector()
        sheng_text = "Manze jana mbogi yetu ilichanga ganji mob sana kujiandaa na shoo."
        self.assertEqual(detector.detect(sheng_text), "sheng_nairobi")

    def test_dialect_detector_sanifu(self):
        detector = DialectDetector()
        sanifu_text = "Kwa mujibu wa taratibu rasmi za serikali, maombi yote yatawasilishwa ofisini."
        self.assertEqual(detector.detect(sanifu_text), "kiswahili_sanifu")

    def test_dialect_detector_kingwana_drc(self):
        detector = DialectDetector()
        kingwana_text = "Niko mu bureau ya Goma, nataka kuludia na sina l'argent ya moto."
        self.assertEqual(detector.detect(kingwana_text), "kingwana_drc")

    def test_dialect_detector_uganda(self):
        detector = DialectDetector()
        uganda_text = "Tugende mu katale ya Kampala, ssebo anataka kulipa kodi ya URA."
        self.assertEqual(detector.detect(uganda_text), "swahili_uganda")

    def test_orchestrator_routing_agriculture(self):
        orchestrator = LughaOrchestrator()
        res = orchestrator.route_and_execute("Je, ni wakati gani sahihi wa kupalilia shamba la mahindi?")
        self.assertEqual(res["routed_domain"], "agriculture")
        self.assertEqual(res["agent_name"], "Kilimo_Advisor_PanAfrica")
        self.assertIn("Kilimo Agent", res["response"])

    def test_orchestrator_routing_finance(self):
        orchestrator = LughaOrchestrator()
        res = orchestrator.route_and_execute("Jinsi ya kufanya reversal ya muamala wa M-Pesa uliokosewa?")
        self.assertEqual(res["routed_domain"], "finance")
        self.assertEqual(res["agent_name"], "Fedha_Services_PanAfrica")

    def test_orchestrator_routing_drc_finance(self):
        orchestrator = LughaOrchestrator()
        res = orchestrator.route_and_execute("Niko Goma Congo nataka kulipa kodi ya DGI kwa franc congolais na Airtel Money.")
        self.assertEqual(res["routed_domain"], "finance")
        self.assertIn("DGI", res["response"])
        self.assertIn("DRC", res["response"])

    def test_orchestrator_routing_kenya_finance(self):
        orchestrator = LughaOrchestrator()
        res = orchestrator.route_and_execute("Niko Nairobi nataka kujua jinsi ya kupata KRA PIN kupitia iTax.")
        self.assertEqual(res["routed_domain"], "finance")
        self.assertIn("KRA", res["response"])

    def test_orchestrator_routing_cultural(self):
        orchestrator = LughaOrchestrator()
        res = orchestrator.route_and_execute("Nini maana ya methali mvumilivu hula mbivu?")
        self.assertEqual(res["routed_domain"], "cultural_linguistic")
        self.assertIn("uvumilivu", res["response"])


if __name__ == "__main__":
    unittest.main()
