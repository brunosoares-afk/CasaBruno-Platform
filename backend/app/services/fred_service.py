from app.services.command_parser import command_parser
from app.services.intent_engine import intent_engine
from app.services.intent_router import intent_router
from app.services.fred_memory import memory
from app.services import memory_service
from app.services.people_service import resolve_person


class FredCore:

    def process(self, command: str, llm_timeout=None, channel: str = "voice", sender: str = None):

        intent_type = None
        result = {"success": False, "message": "Comando vazio."}

        # Fase 6: quem está falando agora. WhatsApp resolve pelo número
        # remetente; voz/web ainda caem no reconhecimento facial da
        # câmera como aproximação (ver people_service.resolve_person).
        person = resolve_person(channel, sender)

        try:

            if not command:
                return result

            # -----------------------------
            # Parser
            # -----------------------------

            parsed = command_parser.parse(command)

            if not parsed:

                result = {
                    "success": False,
                    "message": "Não entendi o comando."
                }
                return result

            memory.remember(
                person,
                "last_command",
                parsed
            )

            # -----------------------------
            # Intent
            # -----------------------------

            intent = intent_engine.parse(parsed, person=person)

            if not intent:

                result = {
                    "success": False,
                    "message": "Nenhuma intenção encontrada.",
                    "command": parsed
                }
                return result

            intent_type = intent.get("type")
            intent["person"] = person

            memory.remember(
                person,
                "last_intent",
                intent_type
            )

            # Contexto pra resolução de pronome ("liga ela" -> intent_engine
            # lê isso pra saber o que "ela" significa). Só grava quando o
            # intent já resolveu um dispositivo de verdade — um comando que
            # também usou pronome (entity_id vindo do fallback) só repete o
            # mesmo valor, não perde o contexto.
            if intent.get("entity_id"):
                memory.remember(person, "last_entity_id", intent["entity_id"])

            # O parser normaliza/remove palavras pra casar comandos de
            # dispositivo por palavra-chave, o que distorce frases naturais
            # (ex: "meu nome é" vira "u no e"). Pra conversa livre com o
            # LLM, usa o texto original em vez do texto tratado.
            if intent_type == "unknown":
                intent["text"] = command
                if llm_timeout is not None:
                    intent["llm_timeout"] = llm_timeout

            # Mesmo motivo do bloco acima: reextrai o tópico a partir do
            # comando original (preserva acento/maiúscula de nomes
            # próprios) em vez do `parsed` já tratado pelo command_parser.
            if intent_type == "knowledge_search":
                intent["query"] = intent_engine.extract_knowledge_topic(command)

            # -----------------------------
            # Router
            # -----------------------------

            result = intent_router.route(intent)

            return result

        except Exception as error:

            result = {
                "success": False,
                "message": "Erro interno no FRED.",
                "error": str(error)
            }
            return result

        finally:

            # Histórico/estatísticas do dashboard — nunca pode quebrar a
            # resposta que já foi computada acima, por isso fica isolado
            # num finally com seu próprio try/except.
            try:
                success = bool(result.get("success")) if isinstance(result, dict) else False
                memory_service.log_activity(channel, command, intent_type, success)
            except Exception:
                pass

    def execute(self, command, channel: str = "web"):

        return self.process(command, channel=channel)

    def ask(self, command, llm_timeout=None, channel: str = "voice", sender: str = None):

        return self.process(command, llm_timeout=llm_timeout, channel=channel, sender=sender)


fred = FredCore()

execute = fred.process
