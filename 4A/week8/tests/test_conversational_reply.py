import os
import unittest
from unittest.mock import MagicMock, patch

import conversational_reply as cr


class TestConversationalReply(unittest.TestCase):
    def test_build_clarification_context_block_non_empty(self):
        s = cr.build_clarification_context_block()
        self.assertIn("Cedar Park", s)
        self.assertIn("jkyog.org", s)

    def test_sanitize_strips_heading_lines_and_caps(self):
        raw = "# Title\n\nHello there.\n" + ("x" * 800)
        out = cr._sanitize_reply(raw)
        self.assertNotIn("# Title", out)
        self.assertLessEqual(len(out), 700)
        self.assertTrue(out.endswith("..."))

    def test_build_conversational_gemini_success(self):
        with patch.object(cr, "_reply_with_gemini", return_value="Try asking about Sunday Satsang!"):
            with patch.object(cr, "_reply_with_ollama_cloud", return_value=None):
                out = cr.build_conversational_clarification_reply(
                    "asdf", "clarification_needed", 0.1, "ctx"
                )
        self.assertEqual(out, "Try asking about Sunday Satsang!")

    def test_build_conversational_ollama_when_gemini_empty(self):
        with patch.object(cr, "_reply_with_gemini", return_value=None):
            with patch.object(cr, "_reply_with_ollama_cloud", return_value="Ollama says hi"):
                out = cr.build_conversational_clarification_reply(
                    "q", "unknown", 0.0, "ctx"
                )
        self.assertEqual(out, "Ollama says hi")

    def test_build_conversational_both_fail_returns_none(self):
        with patch.object(cr, "_reply_with_gemini", return_value=None):
            with patch.object(cr, "_reply_with_ollama_cloud", return_value=None):
                out = cr.build_conversational_clarification_reply(
                    "q", "clarification_needed", 0.2, "ctx"
                )
        self.assertIsNone(out)

    def test_build_conversational_whitespace_only_sanitizes_to_none(self):
        with patch.object(cr, "_reply_with_gemini", return_value="   \n\n  "):
            with patch.object(cr, "_reply_with_ollama_cloud", return_value=None):
                out = cr.build_conversational_clarification_reply(
                    "q", "clarification_needed", 0.2, "ctx"
                )
        self.assertIsNone(out)

    def test_conversational_providers_gemini_client(self):
        fake = MagicMock()
        with patch.object(cr, "_get_gemini_client", return_value=fake):
            self.assertTrue(cr.conversational_providers_configured())

    def test_conversational_providers_ollama_key(self):
        with patch.object(cr, "_get_gemini_client", return_value=None):
            with patch.dict(os.environ, {"OLLAMA_CLOUD_API_KEY": "k"}, clear=False):
                self.assertTrue(cr.conversational_providers_configured())

    def test_conversational_providers_false_without_keys_or_client(self):
        real_getenv = os.getenv

        def getenv_no_ollama(key: str, default=None):
            if key in ("OLLAMA_CLOUD_API_KEY", "OLLAMA_API_KEY", "ZAI_API_KEY"):
                return default
            return real_getenv(key, default)

        with patch.object(cr, "_get_gemini_client", return_value=None):
            with patch("conversational_reply.os.getenv", side_effect=getenv_no_ollama):
                self.assertFalse(cr.conversational_providers_configured())


if __name__ == "__main__":
    unittest.main()
