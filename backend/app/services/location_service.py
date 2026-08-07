from app.services.homeassistant_service import get_states


LOCATION_ENTITY = "sensor.2303era42l_geocoded_location"

TRACKER_ENTITY = "device_tracker.2303era42l"


def current():

    location = None
    tracker = None

    for entity in get_states():

        if entity["entity_id"] == LOCATION_ENTITY:
            location = entity

        elif entity["entity_id"] == TRACKER_ENTITY:
            tracker = entity

    return {

        "address": location["state"] if location else None,

        "tracker_state": tracker["state"] if tracker else None,

        "latitude": tracker.get("attributes", {}).get("latitude") if tracker else None,

        "longitude": tracker.get("attributes", {}).get("longitude") if tracker else None,

        "gps_accuracy": tracker.get("attributes", {}).get("gps_accuracy") if tracker else None

    }


def summary():

    data = current()

    if not data["address"]:

        return {

            "message": "Localização indisponível."

        }

    return {

        "message": data["address"]

    }
