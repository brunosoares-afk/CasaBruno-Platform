from app.core.homeassistant.client import ha_client


class HomeAssistantDevices:

    def all(self):
        return ha_client.states()

    def summary(self):

        entities = self.all()

        domains = {}

        online = 0
        offline = 0

        for entity in entities:

            domain = entity["entity_id"].split(".")[0]

            domains[domain] = domains.get(domain, 0) + 1

            state = str(entity.get("state", "")).lower()

            if state in (
                "unavailable",
                "unknown",
                "offline",
                "not_home"
            ):
                offline += 1
            else:
                online += 1

        return {
            "total": len(entities),
            "online": online,
            "offline": offline,
            "domains": dict(sorted(domains.items()))
        }

    def by_domain(self, domain):

        return [

            e

            for e in self.all()

            if e["entity_id"].startswith(domain + ".")

        ]

    def get(self, entity_id):

        for entity in self.all():

            if entity["entity_id"] == entity_id:
                return entity

        return None


devices = HomeAssistantDevices()
