"""
Unit tests for USSD Gateway and Voice Note Processing.
"""

import unittest
from lughallm.src.channels.ussd import USSDSessionManager
from lughallm.src.audio.voice import SwahiliVoiceProcessor


class TestChannels(unittest.TestCase):

    def setUp(self):
        self.ussd = USSDSessionManager()
        self.voice = SwahiliVoiceProcessor()

    def test_ussd_main_menu(self):
        resp = self.ussd.process_ussd_request(
            session_id="sess_01",
            service_code="*149*00#",
            phone_number="+255712345678",
            text=""
        )
        self.assertTrue(resp.startswith("CON "))
        self.assertIn("Kilimo", resp)
        self.assertIn("Fedha", resp)

    def test_ussd_kilimo_submenu(self):
        resp = self.ussd.process_ussd_request(
            session_id="sess_01",
            service_code="*149*00#",
            phone_number="+255712345678",
            text="1"
        )
        self.assertTrue(resp.startswith("CON "))
        self.assertIn("Mbolea", resp)

    def test_ussd_kilimo_leaf_execution(self):
        resp = self.ussd.process_ussd_request(
            session_id="sess_01",
            service_code="*149*00#",
            phone_number="+255712345678",
            text="1*1"
        )
        self.assertTrue(resp.startswith("END "))
        self.assertIn("Palizi", resp)

    def test_ussd_methali_navigation(self):
        resp = self.ussd.process_ussd_request(
            session_id="sess_01",
            service_code="*149*00#",
            phone_number="+255712345678",
            text="3*1"
        )
        self.assertTrue(resp.startswith("END "))
        self.assertIn("subira", resp.lower())

    def test_voice_transcription_standard(self):
        res = self.voice.transcribe_audio_bytes(
            audio_filename="farm_note.ogg",
            audio_bytes=b"dummy_ogg_bytes_for_testing"
        )
        self.assertEqual(res["language"], "sw")
        self.assertIn("mahindi", res["text"])
        self.assertEqual(res["encoding"], "audio/ogg-opus")

    def test_voice_transcription_sheng(self):
        res = self.voice.transcribe_audio_bytes(
            audio_filename="sheng_voice_note.ogg",
            audio_bytes=b"dummy_sheng_bytes"
        )
        self.assertIn("ganji", res["text"])


if __name__ == "__main__":
    unittest.main()
