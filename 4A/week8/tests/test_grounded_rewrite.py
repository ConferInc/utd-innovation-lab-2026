from unittest.mock import patch

import grounded_reply as gr
from response_builder import build_response, build_response_with_facts


class _StubClient:
    def search_events(self, query, *, limit=10, offset=0):
        return {
            "events": [
                {
                    "id": 42,
                    "name": "Test Holi",
                    "start_datetime": "2030-03-01T18:00:00",
                    "end_datetime": "2030-03-01T21:00:00",
                    "location_name": "Temple Hall",
                    "city": "Cedar Park",
                    "state": "TX",
                    "parking_notes": "Lot A",
                    "food_info": "Prasad",
                    "transportation_notes": "",
                    "source_url": "https://example.com",
                    "registration_url": "https://example.com/reg",
                    "contact_email": "info@example.com",
                    "contact_phone": "555",
                }
            ]
        }

    def get_events(self, *, limit=10, offset=0):
        return {"events": []}

    def get_today(self):
        return {"events": []}

    def get_recurring(self):
        return {"events": []}

    def get_event_by_id(self, event_id):
        return {"event": {}}


def test_build_response_wrapper_matches_with_facts_draft():
    ctx = {"api_client": _StubClient(), "user_message": "parking for holi"}
    classified = {"intent": "logistics", "entities": {"event_name": "Holi"}}
    br = build_response_with_facts(classified, ctx)
    assert build_response(classified, ctx) == br.draft
    assert br.facts is not None
    assert br.facts.get("facts_version") == 1
    assert br.facts.get("response_kind") == "logistics_event"
    assert br.facts["data"]["event"]["name"] == "Test Holi"


def test_temple_static_facts_shape():
    ctx = {"api_client": _StubClient(), "user_message": "Where is the temple?"}
    classified = {"intent": "logistics", "entities": {}}
    br = build_response_with_facts(classified, ctx)
    assert br.facts.get("response_kind") == "temple_static"
    assert "address_line1" in br.facts["data"]["temple"]
    assert br.draft


@patch.object(gr, "_grounded_gemini", return_value="  ONLY PARKING: Lot A  ")
@patch.object(gr, "_grounded_ollama_cloud", return_value=None)
def test_build_grounded_whatsapp_reply_strips_and_returns(mock_ollama, mock_gemini):
    out = gr.build_grounded_whatsapp_reply(
        "parking?",
        "logistics",
        0.9,
        {"response_kind": "logistics_event", "data": {"event": {"parking_notes": "Lot A"}}},
    )
    assert out
    assert "Lot A" in out


@patch.object(gr, "_grounded_gemini", return_value=None)
@patch.object(gr, "_grounded_ollama_cloud", return_value=None)
def test_build_grounded_whatsapp_reply_none_when_providers_fail(mock_ollama, mock_gemini):
    assert (
        gr.build_grounded_whatsapp_reply("hi", "logistics", 0.5, {"data": {}}) is None
    )


def test_grounded_providers_delegates():
    with patch("conversational_reply.conversational_providers_configured", return_value=True):
        assert gr.grounded_reply_providers_configured() is True


def test_rewrite_cap_respects_env(monkeypatch):
    monkeypatch.setenv("LLM_REWRITE_MAX_CHARS", "512")
    assert gr._rewrite_char_cap() == 512
