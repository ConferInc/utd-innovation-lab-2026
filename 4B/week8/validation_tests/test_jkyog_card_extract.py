"""Offline tests for JKYog event card DOM selection."""

from bs4 import BeautifulSoup

from events.scrapers.jkyog import _extract_event_cards


def test_prefers_w_dyn_items_over_event_substring_wrapper() -> None:
    html = """
    <main>
      <div class="w-dyn-list">
        <div class="w-dyn-item">Row A 1450 North Watters Road Allen TX</div>
        <div class="w-dyn-item">Row B 75013 Dallas temple</div>
      </div>
      <div class="some-event-wide-wrapper">whole site chrome repeated</div>
    </main>
    """
    soup = BeautifulSoup(html, "lxml")
    cards = _extract_event_cards(soup)
    assert len(cards) == 2
    assert "Row A" in cards[0].get_text()


def test_filters_oversized_nodes() -> None:
    huge = "x" * 5000
    html = f'<main><div class="w-dyn-item">{huge}</div><div class="w-dyn-item">small 75013</div></main>'
    soup = BeautifulSoup(html, "lxml")
    cards = _extract_event_cards(soup)
    assert len(cards) == 1
    assert "75013" in cards[0].get_text()
