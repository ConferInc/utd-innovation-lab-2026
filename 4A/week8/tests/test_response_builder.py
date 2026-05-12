from response_builder import build_response


class StubEventAPIClient:
    def __init__(self, results_by_query=None):
        self.results_by_query = results_by_query or {}
        self.search_queries = []

    def search_events(self, query, *, limit=10, offset=0):
        self.search_queries.append(query)
        return {"events": self.results_by_query.get(query.lower(), [])}

    def get_events(self, *, limit=10, offset=0):
        return {
            "events": [
                {
                    "id": 999,
                    "name": "Generic Upcoming Event",
                    "start_datetime": "2030-05-20T10:00:00",
                    "end_datetime": "2030-05-20T12:00:00",
                    "location_name": "Main Hall",
                    "city": "Cedar Park",
                    "state": "TX",
                }
            ]
        }

    def get_today(self):
        return {"events": []}

    def get_recurring(self):
        return {"events": []}

    def get_event_by_id(self, event_id):
        raise AssertionError("event id lookup should not be used in this test")


def _event(name: str):
    return {
        "id": 101,
        "name": name,
        "description": "Event description",
        "start_datetime": "2030-05-20T10:00:00",
        "end_datetime": "2030-05-20T12:00:00",
        "location_name": "Temple Hall",
        "city": "Cedar Park",
        "state": "TX",
        "source_url": "https://example.com/event",
    }


def test_event_specific_prefers_cleaned_user_message_over_program_alias():
    client = StubEventAPIClient(
        results_by_query={
            "bhakti kirtan retreat": [_event("Bhakti Kirtan Retreat")],
            "kirtan": [_event("Kirtan Night")],
        }
    )
    reply = build_response(
        {
            "intent": "event_specific",
            "entities": {"program_name": "Kirtan"},
        },
        {
            "api_client": client,
            "user_message": "Tell me about the Bhakti Kirtan Retreat",
        },
    )

    assert client.search_queries == ["bhakti kirtan retreat"]
    assert "Bhakti Kirtan Retreat" in reply
    assert "*upcoming events*" not in reply.lower()


def test_event_specific_no_results_does_not_fall_back_to_generic_upcoming_list():
    client = StubEventAPIClient(results_by_query={})
    reply = build_response(
        {
            "intent": "event_specific",
            "entities": {},
        },
        {
            "api_client": client,
            "user_message": "Tell me about Hanuman Jayanti",
        },
    )

    assert client.search_queries == ["hanuman jayanti"]
    assert "could not find any matching events" in reply.lower()
    assert "*upcoming events*" not in reply.lower()
