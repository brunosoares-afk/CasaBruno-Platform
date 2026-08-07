from app.services.homeassistant_service import get_states


def normalize(text: str):

    return (
        text.lower()
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ã", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def all_devices():

    devices = []

    for entity in get_states():

        devices.append({

            "entity_id": entity.get("entity_id"),

            "name": entity.get(
                "attributes",
                {}
            ).get(
                "friendly_name",
                entity.get("entity_id")
            ),

            "state": entity.get("state"),

            "attributes": entity.get(
                "attributes",
                {}
            )
        })

    return devices


def get_entity(entity_id):

    for entity in get_states():

        if entity["entity_id"] == entity_id:

            return entity

    return None


def search(text):

    text = normalize(text)

    result = []

    for entity in all_devices():

        name = normalize(entity["name"])
        entity_id = normalize(entity["entity_id"])

        if text in name or text in entity_id:

            result.append(entity)

    return result


def switches():

    return [

        e

        for e in all_devices()

        if e["entity_id"].startswith("switch.")
    ]


def lights():

    return [

        e

        for e in all_devices()

        if e["entity_id"].startswith("light.")
    ]


def sensors():

    return [

        e

        for e in all_devices()

        if e["entity_id"].startswith("sensor.")
    ]


def trackers():

    return [

        e

        for e in all_devices()

        if e["entity_id"].startswith("device_tracker.")
    ]
