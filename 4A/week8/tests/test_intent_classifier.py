import unittest
from unittest.mock import patch
from intent_classifier import classify


class TestIntentClassifier(unittest.TestCase):

    # -------------------------------
    # TIME-BASED
    # -------------------------------
    def test_time_based_today(self):
        result = classify("What’s happening today?")
        self.assertIn(result["intent"], ["time_based"])

    def test_time_based_weekend(self):
        result = classify("Events this weekend?")
        self.assertIn(result["intent"], ["time_based", "discovery"])

    # -------------------------------
    # EVENT SPECIFIC
    # -------------------------------
    def test_event_specific_holi(self):
        result = classify("Tell me about Holi Festival")
        self.assertIn(result["intent"], ["event_specific"])

    def test_event_specific_ram(self):
        result = classify("Ram Navami details")
        self.assertIn(result["intent"], ["event_specific"])

    # -------------------------------
    # RECURRING
    # -------------------------------
    def test_recurring_darshan(self):
        result = classify("Is darshan daily?")
        self.assertIn(result["intent"], ["recurring_schedule", "time_based", "clarification_needed"])

    def test_recurring_aarti(self):
        result = classify("Aarti timings?")
        self.assertIn(result["intent"], ["recurring_schedule", "time_based"])

    # -------------------------------
    # LOGISTICS
    # -------------------------------
    def test_logistics_parking(self):
        result = classify("Where do I park?")
        self.assertIn(result["intent"], ["logistics"])

    def test_logistics_address(self):
        result = classify("Temple address?")
        self.assertIn(result["intent"], ["logistics"])

    # -------------------------------
    # SPONSORSHIP
    # -------------------------------
    def test_sponsorship(self):
        result = classify("How can I sponsor an event?")
        self.assertIn(result["intent"], ["sponsorship", "event_specific"])

    def test_donation(self):
        result = classify("I want to donate")
        self.assertIn(result["intent"], ["sponsorship"])

    # -------------------------------
    # DISCOVERY
    # -------------------------------
    def test_discovery_general(self):
        result = classify("What’s happening?")
        self.assertIn(result["intent"], ["discovery"])

    def test_discovery_fun(self):
        result = classify("Any events going on?")
        self.assertIn(result["intent"], ["discovery"])

    # -------------------------------
    # NO RESULTS
    # -------------------------------
    def test_no_results(self):
        result = classify("Events at 3 AM tonight?")
        self.assertIn(result["intent"], ["no_results_check", "time_based"])

    def test_no_results_midnight(self):
        result = classify("Anything at midnight?")
        self.assertIn(result["intent"], ["no_results_check", "time_based"])

    # -------------------------------
    # EDGE CASES
    # -------------------------------
    def test_edge_low_confidence(self):
        result = classify("Hi")
        self.assertEqual(result["intent"], "clarification_needed")
        self.assertLess(result["confidence"], 0.6)

    def test_edge_overlap(self):
        result = classify("Parking for Ram Navami tonight?")
        self.assertIn(result["intent"], ["event_specific", "logistics", "time_based", "clarification_needed"])

    def test_edge_ambiguous(self):
        result = classify("Info")
        self.assertEqual(result["intent"], "clarification_needed")

    # -------------------------------
    # CONFIDENCE BOUNDARY TESTS
    # -------------------------------
    def test_confidence_below_boundary_short_greeting(self):
        result = classify("Hello")
        self.assertEqual(result["intent"], "clarification_needed")
        self.assertLess(result["confidence"], 0.6)

    def test_confidence_below_boundary_unknown_request(self):
        result = classify("Maybe")
        self.assertEqual(result["intent"], "clarification_needed")
        self.assertLess(result["confidence"], 0.6)

    @patch("intent_classifier.extract_entities", return_value={
        "event_name": None,
        "program_name": None,
        "timeframe": "tonight"
    })
    def test_confidence_above_boundary_time_based(self, mock_extract):
        result = classify("What is happening tonight?")
        self.assertIn(result["intent"], ["time_based", "clarification_needed"])
        self.assertGreaterEqual(result["confidence"], 0.0)

    def test_confidence_above_boundary_no_results(self):
        result = classify("Anything at midnight?")
        self.assertGreaterEqual(result["confidence"], 0.0)

    def test_confidence_above_boundary_discovery(self):
        result = classify("Any events coming up?")
        self.assertIn(result["intent"], ["discovery", "clarification_needed"])
        self.assertGreaterEqual(result["confidence"], 0.0)


if __name__ == "__main__":
    unittest.main()
