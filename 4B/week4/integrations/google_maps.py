"""
Google Maps Directions API - Temple Directions
Subodh Krishna Nikumbh - Week 3 JKYog WhatsApp Bot
"""

import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import googlemaps

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if GOOGLE_MAPS_API_KEY:
    _client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
else:
    _client = None


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def get_directions_text(origin: str, destination: str, mode: str = "driving") -> str:
    if not _client:
        return f"🗺️ Directions from {origin} to {destination} (API key required)"
    
    try:
        result: List[Dict[str, Any]] = _client.directions(
            origin=origin,
            destination=destination,
            mode=mode,
        )
        
        if not result:
            return "❌ Could not find directions for that route."
        
        steps = result[0]["legs"][0]["steps"]
        lines = []
        total_distance = result[0]["legs"][0]["distance"]["text"]
        total_duration = result[0]["legs"][0]["duration"]["text"]
        
        lines.append(f"🗺️ {total_distance} • {total_duration}")
        for idx, step in enumerate(steps, start=1):
            instruction = _strip_html(step["html_instructions"])
            distance = step["distance"]["text"]
            lines.append(f"{idx}. {instruction} ({distance})")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Directions service unavailable. Error: {str(e)}"


def get_temple_directions_from_user_location(
    user_location: str,
    temple_address: str,
    mode: str = "driving",
) -> str:
    """Rohan's bot entrypoint - user location → temple"""
    return get_directions_text(origin=user_location, destination=temple_address, mode=mode)
