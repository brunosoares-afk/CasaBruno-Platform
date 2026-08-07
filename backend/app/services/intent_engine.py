from app.services.device_registry import registry


class IntentEngine:

    # ======================================================
    # ENTRADA PRINCIPAL
    # ======================================================

    def parse(self, command: str):

        if not command:
            return {"type": "unknown"}

        cmd = registry.normalize(command)

        # ==================================================
        # SISTEMA
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "home assistant",
                "status home assistant"
            ]
        ):
            return {
                "type": "homeassistant_status"
            }

        # ==================================================
        # REGISTRY
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "atualizar dispositivos",
                "atualizar registry",
                "recarregar dispositivos"
            ]
        ):
            return {
                "type": "registry_refresh"
            }

        if self.contains_any(
            cmd,
            [
                "listar dispositivos",
                "mostrar dispositivos",
                "quais dispositivos",
                "dispositivos"
            ]
        ):
            return {
                "type": "device_list"
            }

        # ==================================================
        # AÇÕES DE DISPOSITIVOS
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "ligar",
                "acender",
                "ativar",
                "abrir"
            ]
        ):
            return self.device_action(cmd, "turn_on")

        if self.contains_any(
            cmd,
            [
                "desligar",
                "apagar",
                "desativar",
                "fechar"
            ]
        ):
            return self.device_action(cmd, "turn_off")

        # ==================================================
        # STATUS
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "status",
                "estado",
                "situacao",
                "situação"
            ]
        ):
            return self.device_status(cmd)

        return {
            "type": "unknown"
        }

    # ======================================================
    # DEVICE ACTION
    # ======================================================

    def device_action(self, cmd, action):

        try:
            devices = registry.search(cmd)
        except Exception:
            return {"type": "unknown"}

        if not devices:
            return {"type": "unknown"}

        entity = devices[0]

        return {
            "type": "device_action",
            "action": action,
            "entity_id": entity.get("entity_id")
        }

    # ======================================================
    # DEVICE STATUS
    # ======================================================

    def device_status(self, cmd):

        try:
            devices = registry.search(cmd)
        except Exception:
            return {"type": "unknown"}

        if not devices:
            return {"type": "unknown"}

        entity = devices[0]

        return {
            "type": "device_status",
            "entity_id": entity.get("entity_id")
        }

    # ======================================================
    # UTIL
    # ======================================================

    def contains_any(self, text, words):

        if not text:
            return False

        for word in words:
            if word in text:
                return True

        return False


intent_engine = IntentEngine()
