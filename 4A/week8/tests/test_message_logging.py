"""Tests for Twilio phone normalization (Team 4B auth parity)."""

from database.message_logging import normalize_twilio_phone


def test_normalize_twilio_phone_strips_prefix_and_plus():
    assert normalize_twilio_phone("whatsapp:+15551234567") == "15551234567"
    assert normalize_twilio_phone("+15551234567") == "15551234567"
    assert normalize_twilio_phone("15551234567") == "15551234567"
