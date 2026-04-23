import unittest
from intent_classifier import classify


class TestIntentClassifier(unittest.TestCase):

    # TIME-BASED
    def test_time_based_today(self):
        self.assertEqual(classify("What’s happening today?")["intent"], "time_based")

    def test_time_based_weekend(self):
        self.assertEqual(classify("Events this weekend?")["intent"], "time_based")

    # EVENT SPECIFIC
    def test_event_specific_holi(self):
        self.assertEqual(classify("Tell me about Holi Festival")["intent"], "event_specific")

    def test_event_specific_ram(self):
        self.assertEqual(classify("Ram Navami details")["intent"], "event_specific")

    # RECURRING
    def test_recurring_darshan(self):
        self.assertEqual(classify("When is darshan?")["intent"], "recurring_schedule")

    def test_recurring_aarti(self):
        self.assertEqual(classify("Aarti timings?")["intent"], "recurring_schedule")

    # LOGISTICS
    def test_logistics_parking(self):
        self.assertEqual(classify("Where do I park?")["intent"], "logistics")

    def test_logistics_address(self):
        self.assertEqual(classify("Temple address?")["intent"], "logistics")

    # SPONSORSHIP
    def test_sponsorship(self):
        self.assertEqual(classify("How can I sponsor an event?")["intent"], "sponsorship")

    def test_donation(self):
        self.assertEqual(classify("I want to donate")["intent"], "sponsorship")

    # DISCOVERY
    def test_discovery_general(self):
        self.assertEqual(classify("What’s happening?")["intent"], "discovery")

    def test_discovery_fun(self):
        self.assertEqual(classify("Any events going on?")["intent"], "discovery")

    # NO RESULTS
    def test_no_results(self):
        self.assertEqual(classify("Events at 3 AM tonight?")["intent"], "no_results_check")

    def test_no_results_midnight(self):
        self.assertEqual(classify("Anything at midnight?")["intent"], "no_results_check")

    # EDGE CASES
    def test_edge_low_confidence(self):
        self.assertEqual(classify("Hi")["intent"], "clarification_needed")

    def test_edge_overlap(self):
        result = classify("Parking for Ram Navami tonight?")
        self.assertIn(result["intent"], ["event_specific", "logistics", "time_based"])

    def test_edge_ambiguous(self):
        self.assertEqual(classify("Info")["intent"], "clarification_needed")

    # CONFIDENCE BOUNDARY
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
        self.assertEqual(result["intent"], "time_based")
        self.assertGreater(result["confidence"], 0.6)

    def test_confidence_above_boundary_no_results(self):
        result = classify("Anything at midnight?")
        self.assertEqual(result["intent"], "no_results_check")
        self.assertGreater(result["confidence"], 0.6)

    def test_confidence_above_boundary_discovery(self):
        result = classify("Any events coming up?")
        self.assertEqual(result["intent"], "discovery")
        self.assertGreater(result["confidence"], 0.6)


if __name__ == "__main__":
    unittest.main()
