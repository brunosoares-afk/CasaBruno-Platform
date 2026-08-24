from app.core.homeassistant.client import ha_client
from app.core.logger.logger import logger
from app.core.events.event_manager import event_manager
from app.services import alexa_service, homeassistant_service, tuya_service, scenes_service, ptz_service

_MEDIA_SERVICE_TO_COMMAND = {
    "media_next_track": "next",
    "media_previous_track": "previous",
    "media_stop": "stop",
}


class HomeAssistantServices:

    def list(self):
        # Mesmo motivo do devices.py: HA não existe mais, ha_client.services()
        # sempre falha, sem try/except isso derrubava a rota inteira.
        try:
            return ha_client.services()
        except Exception:
            return []

    def call(
        self,
        domain,
        service,
        data=None
    ):

        if data is None:
            data = {}

        entity_id = data.get("entity_id")

        if tuya_service.is_managed(entity_id) and service in ("turn_on", "turn_off"):
            device_key = tuya_service.device_key_for(entity_id)
            ok = tuya_service.turn_on(device_key) if service == "turn_on" else tuya_service.turn_off(device_key)
            result = {"success": ok, "local": "tuya"}
        elif domain == "icsee_ptz" and service == "move" and ptz_service.is_managed(entity_id):
            device_key = ptz_service.device_key_for(entity_id)
            ok = ptz_service.move(
                device_key,
                data.get("cmd", "Stop"),
                step=data.get("step", 5),
                preset=data.get("preset", -1),
            )
            result = {"success": ok, "local": "dvrip"}
        elif scenes_service.is_managed(entity_id) and service == "turn_on":
            result = scenes_service.run(entity_id)
        elif domain == "media_player" and alexa_service.is_managed(entity_id):
            ok = self._call_alexa_media(entity_id, service, data)
            result = {"success": ok, "local": "alexa"}
        else:
            # Fallback pra qualquer entidade que não caia em nenhum dos
            # roteamentos locais acima (tuya/ptz/scenes/alexa) — hoje
            # nenhuma entidade viva bate aqui, mas se uma nova cair sem
            # roteamento dedicado, isso batia direto no HA morto e
            # explodia sem mensagem útil (mesma armadilha do _push, ver
            # [[casa-bruno-push-notify-bug-2026-08-23]]).
            try:
                result = ha_client.call_service(
                    domain,
                    service,
                    data
                )
            except Exception as e:
                result = {"success": False, "error": str(e)}

        logger.info(
            "homeassistant",
            f"{domain}.{service}"
        )

        event_manager.emit(
            "ha.service_called",
            {
                "domain": domain,
                "service": service,
                "data": data,
                "result": result,
            }
        )

        return result

    def _call_alexa_media(self, entity_id, service, data):
        if service == "volume_set":
            return alexa_service.set_volume(entity_id, data.get("volume_level", 0))

        if service == "media_play_pause":
            # Sem toggle na lib — decide play/pause pelo estado atual. Usa
            # o snapshot do relay (homeassistant_service.get_states()), não
            # ha_client.states() cru — esse não sobrevive à HA desligada
            # (Fase 10), o snapshot sim.
            states = homeassistant_service.get_states()
            entity = next((s for s in states if s.get("entity_id") == entity_id), None)
            command = "pause" if entity and entity.get("state") == "playing" else "play"
            return alexa_service.media_command(entity_id, command)

        command = _MEDIA_SERVICE_TO_COMMAND.get(service)
        if command:
            return alexa_service.media_command(entity_id, command)

        return False

    def turn_on(self, entity_id):

        return self.call(
            "homeassistant",
            "turn_on",
            {
                "entity_id": entity_id
            }
        )

    def turn_off(self, entity_id):

        return self.call(
            "homeassistant",
            "turn_off",
            {
                "entity_id": entity_id
            }
        )


services = HomeAssistantServices()
