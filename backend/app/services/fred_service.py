from app.services.command_parser import command_parser
from app.services.intent_engine import intent_engine
from app.services.intent_router import intent_router
from app.services.fred_memory import memory


class FredCore:

    def process(self, command: str):

        try:

            if not command:

                return {
                    "success": False,
                    "message": "Comando vazio."
                }

            # -----------------------------
            # Parser
            # -----------------------------

            parsed = command_parser.parse(command)

            if not parsed:

                return {
                    "success": False,
                    "message": "Não entendi o comando."
                }

            memory.remember(
                "last_command",
                parsed
            )

            # -----------------------------
            # Intent
            # -----------------------------

            intent = intent_engine.parse(parsed)

            if not intent:

                return {
                    "success": False,
                    "message": "Nenhuma intenção encontrada.",
                    "command": parsed
                }

            memory.remember(
                "last_intent",
                intent.get("type")
            )

            # -----------------------------
            # Router
            # -----------------------------

            response = intent_router.route(intent)

            return response

        except Exception as error:

            return {
                "success": False,
                "message": "Erro interno no FRED.",
                "error": str(error)
            }

    def execute(self, command):

        return self.process(command)

    def ask(self, command):

        return self.process(command)


fred = FredCore()

execute = fred.process
