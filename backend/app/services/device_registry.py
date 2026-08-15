from app.services.homeassistant_service import get_states


class DeviceRegistry:

    # Palavras que não devem contar como "match" na busca por palavra —
    # sem isso, "do"/"da"/"a" batem em qualquer nome que tenha essas
    # letras soltas (ex: "do not disturb"), e verbos de comando
    # (ligar/status/etc) não são parte do nome do dispositivo.
    STOPWORDS = {
        "a", "o", "as", "os", "de", "da", "do", "das", "dos",
        "um", "uma", "e", "em", "no", "na", "nos", "nas",
        "para", "por", "com",
        "status", "estado", "situacao", "situação", "qual", "quais",
        "ligar", "desligar", "acender", "apagar",
        "ativar", "desativar", "abrir", "fechar",
    }

    def __init__(self):
        self.entities = []
        self.loaded = False

    # ======================================================
    # LOAD
    # ======================================================

    def load(self):

        try:
            self.entities = get_states()
            self.loaded = True

        except Exception:
            self.entities = []
            self.loaded = False

        return self.loaded

    def refresh(self):
        return self.load()

    def ensure_loaded(self):

        if not self.loaded:
            self.load()

    def is_loaded(self):
        return self.loaded

    def count(self):

        self.ensure_loaded()

        return len(self.entities)

    def summary(self):

        self.ensure_loaded()

        domains = {}

        for entity in self.entities:

            domain = entity["entity_id"].split(".")[0]

            domains[domain] = domains.get(domain, 0) + 1

        return {
            "loaded": self.loaded,
            "entities": len(self.entities),
            "domains": domains,
        }

    def all(self):

        self.ensure_loaded()

        return self.entities

    def by_entity_id(self, entity_id):

        self.ensure_loaded()

        entity_id = self.normalize(entity_id)

        for entity in self.entities:

            if self.normalize(entity["entity_id"]) == entity_id:
                return entity

        return None

    def by_domain(self, domain):

        self.ensure_loaded()

        prefix = domain.lower() + "."

        return [
            entity
            for entity in self.entities
            if entity["entity_id"].startswith(prefix)
        ]

    # ======================================================
    # SEARCH
    # ======================================================

    def search(self, text):

        self.ensure_loaded()

        query = self.normalize(text)

        scored = []

        for entity in self.entities:

            score = self.score_entity(entity, query)

            if score > 0:
                scored.append((score, entity))

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [entity for score, entity in scored]

    # ======================================================
    # SCORE
    # ======================================================

    def score_entity(self, entity, query):

        entity_id = self.normalize(
            entity.get("entity_id", "")
        )

        friendly = self.normalize(
            entity.get(
                "attributes",
                {}
            ).get(
                "friendly_name",
                ""
            )
        )

        domain = entity.get(
            "entity_id",
            ""
        ).split(".")[0]

        aliases = [
            self.normalize(alias)
            for alias in entity.get(
                "attributes",
                {}
            ).get(
                "aliases",
                []
            )
        ]

        score = 0

        # ==================================================
        # MATCH EXATO
        # ==================================================

        if query == entity_id:
            score += 300

        if query == friendly:
            score += 400

        # ==================================================
        # CONTAINS
        # ==================================================

        if query in entity_id:
            score += 120

        if query in friendly:
            score += 180

        # ==================================================
        # PALAVRAS
        # ==================================================

        for word in query.split():

            if len(word) <= 2 or word in self.STOPWORDS:
                continue

            if word in entity_id:
                score += 30

            if word in friendly:
                score += 60

            for alias in aliases:

                if word in alias:
                    score += 40

        # ==================================================
        # ALIASES
        # ==================================================

        for alias in aliases:

            if query == alias:
                score += 200

            elif query in alias:
                score += 100

        # ==================================================
        # PRIORIDADE DOS DOMÍNIOS
        #
        # Só entra como desempate DEPOIS de já haver algum match de
        # texto real — se entrasse incondicionalmente, qualquer light/
        # switch da casa teria score > 0 mesmo sem nenhuma palavra em
        # comum com o pedido, e o Fred acabaria "encontrando" e
        # acionando um dispositivo qualquer para comandos que não
        # batem com nada (ex: "ligar luz da sala" sem luz nenhuma
        # cadastrada pegava o switch da cozinha por padrão).
        # ==================================================

        if score == 0:
            return 0

        domain_bonus = {
            "light": 500,
            "switch": 450,
            "cover": 430,
            "fan": 420,
            "climate": 410,
            "lock": 400,
            "scene": 200,
            "automation": 100,
            "select": -500,
            "sensor": -600,
        }.get(domain, 0)

        return score + domain_bonus

    # ======================================================
    # NORMALIZE
    # ======================================================

    @staticmethod
    def normalize(text):

        return (
            str(text)
            .lower()
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
            .replace("_", " ")
            .strip()
        )


registry = DeviceRegistry()
