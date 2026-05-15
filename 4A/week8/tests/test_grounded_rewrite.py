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
    assert br.facts.get("user_message_echo") == "parking for holi"


def test_temple_static_facts_shape():
    ctx = {"api_client": _StubClient(), "user_message": "Where is the temple?"}
    classified = {"intent": "logistics", "entities": {}}
    br = build_response_with_facts(classified, ctx)
    assert br.facts.get("response_kind") == "temple_static"
    assert "address_line1" in br.facts["data"]["temple"]
    assert len(br.facts["data"]["temple"]["temple_hours_by_day_ct"]) == 7
    assert len(br.facts["data"]["temple"]["kitchen_hours_by_day_ct"]) == 4
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


def test_formatting_guidance_event_list_multi():
    facts = {
        "response_kind": "event_list",
        "data": {
            "events": [{"name": "A"}, {"name": "B"}],
        },
    }
    text = gr._formatting_guidance(facts)
    assert "event_list" in text
    assert "2 event" in text
    assert "numbered list" in text
    assert "subordinate" in text.lower()


def test_formatting_guidance_api_error_no_bullets():
    facts = {"response_kind": "api_client_error", "data": {"message": "api_client_error"}}
    text = gr._formatting_guidance(facts)
    assert "api_client_error" in text
    assert "no decorative" in text
    assert "subordinate" in text.lower()


def test_format_grounded_user_block_appends_formatting_section():
    facts = {"response_kind": "no_results", "data": {"query": "zzz"}}
    block = gr._format_grounded_user_block("any events?", "event_list", 0.4, facts)
    assert "Your reply must directly address the user's question below." in block
    assert "FACTS (JSON" in block
    assert "Internal route" in block
    assert "'event_list'" in block or "event_list" in block
    assert block.index("FACTS (JSON") < block.index("Internal route")
    assert "Formatting (instructions only" in block
    assert "no matching events" in block.lower() or "No matching" in block
    assert "subordinate" in block.lower()


def test_format_grounded_user_block_classifier_not_before_facts():
    facts = {"response_kind": "event_list", "data": {"events": []}}
    block = gr._format_grounded_user_block("parking?", "logistics", 0.9, facts)
    assert "Classifier intent:" not in block
    assert "What the user wrote:" in block
