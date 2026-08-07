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
