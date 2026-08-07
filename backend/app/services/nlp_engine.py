import re

from app.services.device_registry import registry


class NLPEngine:

    def __init__(self):

        self.action_words = {
            "ligar": "turn_on",
            "acender": "turn_on",
            "ativar": "turn_on",
            "abrir": "open_cover",
            "desligar": "turn_off",
            "apagar": "turn_off",
            "fechar": "close_cover",
            "trancar": "lock",
            "destrancar": "unlock",
            "alternar": "toggle",
            "toggle": "toggle",
        }

        self.status_words = [
            "estado",
            "status",
            "ligado",
            "desligado",
            "aceso",
            "apagado",
            "aberto",
            "fechado",
        ]

        self.list_words = [
            "listar",
            "listar todos",
            "mostrar",
            "mostrar todos",
            "quais",
            "lista",
        ]

        self.refresh_words = [
            "atualizar dispositivos",
            "recarregar dispositivos",
            "sincronizar dispositivos",
            "atualizar registry",
            "refresh registry",
        ]

        self.homeassistant_words = [
            "home assistant",
            "status home assistant",
            "ha online",
            "ha offline",
        ]

        self.stop_words = {
            "a",
            "o",
            "os",
            "as",
            "da",
            "do",
            "das",
            "dos",
            "de",
            "em",
            "na",
            "no",
            "nas",
            "nos",
            "por",
            "para",
            "com",
            "um",
            "uma",
            "uns",
            "umas",
        }

    # ======================================================
    # ENTRADA
    # ======================================================

    def parse(self, command):

        registry.ensure_loaded()

        text = self.normalize(command)

        intent = self.refresh_parser(text)

        if intent:
            return intent

        intent = self.homeassistant_parser(text)

        if intent:
            return intent

        intent = self.list_parser(text)

        if intent:
            return intent

        intent = self.action_parser(text)

        if intent:
            return intent

        intent = self.status_parser(text)

        if intent:
            return intent

        return None

    # ======================================================
    # ACTION
    # ======================================================

    def action_parser(self, text):

        service = None

        action_word = None

        for word, svc in self.action_words.items():

            if word in text:

                service = svc
                action_word = word
                break

        if service is None:
            return None

        query = text.replace(action_word, " ")

        query = self.clean_query(query)

        devices = registry.search(query)

        if not devices:

            return {
                "type": "device_not_found",
                "query": query
            }

        if len(devices) == 1:

            return {
                "type": "device_action",
                "service": service,
                "entity_id": devices[0]["entity_id"]
            }

        best = devices[0]

        return {
            "type": "device_action",
            "service": service,
            "entity_id": best["entity_id"]
        }

    # ======================================================
    # STATUS
    # ======================================================

    def status_parser(self, text):

        if not any(word in text for word in self.status_words):
            return None

        query = text

        for word in self.status_words:
            query = query.replace(word, " ")

        query = self.clean_query(query)

        devices = registry.search(query)

        if not devices:

            return {
                "type": "device_not_found",
                "query": query
            }

        return {
            "type": "device_status",
            "entity_id": devices[0]["entity_id"]
        }

    # ======================================================
    # LISTA
    # ======================================================

    def list_parser(self, text):

        for word in self.list_words:

            if word in text:

                query = text.replace(word, " ")

                query = self.clean_query(query)

                if query == "":

                    return {
                        "type": "device_list",
                        "devices": registry.all()
                    }

                devices = registry.search(query)

                return {
                    "type": "device_list",
                    "count": len(devices),
                    "devices": devices
                }

        return None

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh_parser(self, text):

        for word in self.refresh_words:

            if word in text:

                return {
                    "type": "registry_refresh"
                }

        return None

    # ======================================================
    # HOME ASSISTANT
    # ======================================================

    def homeassistant_parser(self, text):

        for word in self.homeassistant_words:

            if word in text:

                return {
                    "type": "homeassistant_status"
                }

        return None

    # ======================================================
    # QUERY
    # ======================================================

    def clean_query(self, text):

        words = []

        for word in text.split():

            if word in self.stop_words:
                continue

            words.append(word)

        return " ".join(words).strip()

    # ======================================================
    # NORMALIZE
    # ======================================================

    @staticmethod
    def normalize(text):

        text = str(text).lower()

        replaces = {
            "á": "a",
            "à": "a",
            "â": "a",
            "ã": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
            "_": " ",
        }

        for a, b in replaces.items():
            text = text.replace(a, b)

        text = re.sub(r"[^a-z0-9 ]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()


nlp_engine = NLPEngine()
