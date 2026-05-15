"""Scripted pastoral replies (guru contact, spiritual peace) — see main.py."""

import unittest

from intent_classifier import pastoral_guidance_kind


class TestPastoralGuidanceKind(unittest.TestCase):
    def test_guru_contact_phrase(self):
        self.assertEqual(
            pastoral_guidance_kind("how can i talk to the baba?", {}),
            "guru_contact",
        )

    def test_spiritual_peace_phrase(self):
        self.assertEqual(
            pastoral_guidance_kind("how can i find peace?", {}),
            "spiritual_peace",
        )

    def test_suppressed_when_event_target(self):
        self.assertIsNone(
            pastoral_guidance_kind(
                "how can i find peace?",
                {"event_name": "Holi"},
            )
        )


if __name__ == "__main__":
    unittest.main()
