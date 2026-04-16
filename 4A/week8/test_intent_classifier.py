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


if __name__ == "__main__":
    unittest.main()
