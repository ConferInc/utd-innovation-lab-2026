from response_builder_2 import _format_event_list, _truncate_whatsapp, WHATSAPP_CHAR_LIMIT


def make_fake_event(index: int) -> dict:
    return {
        "name": f"Very Long Test Event Name Number {index} " + ("Spiritual Gathering " * 20),
        "start_datetime": "2026-04-25T18:30:00",
        "location_name": "Radha Krishna Temple of Dallas " + ("Main Hall " * 10),
        "city": "Allen",
        "state": "TX",
        "postal_code": "75013",
        "timezone": "CST",
    }



def main() -> None:
    fake_events = [make_fake_event(i) for i in range(1, 21)]

    long_text = _format_event_list(fake_events, "artificial long event list")
    truncated_text = _truncate_whatsapp(long_text)

    print("Original length:", len(long_text))
    print("Final length:", len(truncated_text))
    print("Within WhatsApp limit:", len(truncated_text) <= WHATSAPP_CHAR_LIMIT)
    print("Truncation marker present:", "... [truncated]" in truncated_text)
    print("\n--- FINAL OUTPUT PREVIEW ---\n")
    print(truncated_text)


if __name__ == "__main__":
    main()
