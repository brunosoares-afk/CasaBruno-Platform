from app.services.intent_handlers import handlers
from app.services.response_builder import response_builder


class IntentRouter:

    def __init__(self):

        self.handlers = {}

        self.register_defaults()

    # ======================================================
    # REGISTRO
    # ======================================================

    def register(self, intent_type, handler):

        self.handlers[intent_type] = handler

    # ======================================================
    # HANDLERS PADRÃO
    # ======================================================

    def register_defaults(self):

        self.register(
            "device_action",
            handlers.device_action
        )

        self.register(
            "device_status",
            handlers.device_status
        )

        self.register(
            "device_not_found",
            handlers.device_not_found
        )

        self.register(
            "multiple_devices",
            handlers.multiple_devices
        )

        self.register(
            "device_list",
            handlers.device_list
        )

        self.register(
            "registry_refresh",
            handlers.registry_refresh
        )

        self.register(
            "homeassistant_status",
            handlers.homeassistant_status
        )

        self.register(
            "domain_search",
            handlers.domain_search
        )

        self.register(
            "sensor_query",
            handlers.sensor_query
        )

        self.register(
            "knowledge_search",
            handlers.knowledge_search
        )

        self.register(
            "network_status",
            handlers.network_status
        )

        self.register(
            "weather_query",
            handlers.weather_query
        )

        self.register(
            "time_query",
            handlers.time_query
        )

        self.register(
            "house_status",
            handlers.house_status
        )

        self.register(
            "presence_query",
            handlers.presence_query
        )

        self.register(
            "phone_query",
            handlers.phone_query
        )

        self.register(
            "server_system_query",
            handlers.server_system_query
        )

        self.register(
            "set_preference",
            handlers.set_preference
        )

        self.register(
            "set_favorite_device",
            handlers.set_favorite_device
        )

        self.register(
            "favorite_device_query",
            handlers.favorite_device_query
        )

        self.register(
            "memory_summary",
            handlers.memory_summary
        )

        self.register(
            "confirmed_action",
            handlers.confirmed_action
        )

        self.register(
            "confirmation_declined",
            handlers.confirmation_declined
        )

        self.register(
            "ha_system_query",
            handlers.ha_system_query
        )

        self.register(
            "backend_status",
            handlers.backend_status
        )

        self.register(
            "unknown",
            handlers.llm_fallback
        )

    # ======================================================
    # ROUTER
    # ======================================================

    def route(self, intent):

        try:

            if intent is None:

                return {

                    "success": False,

                    "message": "Nenhuma intenção identificada."

                }

            intent_type = intent.get(
                "type"
            )

            handler = self.handlers.get(
                intent_type
            )

            if handler is None:

                return {

                    "success": False,

                    "message": f"Intent '{intent_type}' não suportada."

                }

            result = handler(
                intent
            )

            return response_builder.build(
                result
            )

        except Exception as error:

            return {

                "success": False,

                "message": "Erro no Intent Router.",

                "error": str(error)

            }

    # ======================================================
    # UTILITÁRIOS
    # ======================================================

    def list_handlers(self):

        return sorted(
            self.handlers.keys()
        )


intent_router = IntentRouter()
