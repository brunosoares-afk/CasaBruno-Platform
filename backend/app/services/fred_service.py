import re

from app.services.command_parser import command_parser
from app.services.intent_engine import intent_engine
from app.services.intent_router import intent_router
from app.services.fred_memory import memory
from app.services import memory_service
from app.services.people_service import resolve_person


# Fase 7: comando composto ("liga a luz da sala e desliga o ventilador").
# Só separa em " e "/" e depois "/", " — cada pedaço tem que resolver
# sozinho pra um device_action limpo (mesma validação de um comando único)
# ANTES de qualquer um deles ser executado. Se um pedaço qualquer for
# ambíguo/não encontrado/outro tipo de intent, o split inteiro é abortado
# e o comando original inteiro cai no caminho de sempre (single intent) —
# nunca executa metade de um comando composto que não entendeu por inteiro.
_COMPOUND_SPLIT_RE = re.compile(r"\s+e\s+depois\s+|\s+depois\s+|\s+e\s+|\s*,\s*", re.IGNORECASE)


class FredCore:

    def _resolve_device_action(self, segment, person):
        """Roda o mesmo parser+intent_engine do caminho único num pedaço de
        comando composto. Só retorna algo se o pedaço resolver limpo pra um
        device_action de verdade — qualquer outro tipo (unknown, ambíguo,
        não encontrado, query) faz retornar None, o que aborta o split
        inteiro em _try_compound."""

        parsed = command_parser.parse(segment)
        if not parsed:
            return None

        intent = intent_engine.parse(parsed, person=person)
        if not intent or intent.get("type") != "device_action":
            return None

        intent["person"] = person
        return intent

    def _try_compound(self, command, person):
        """Tenta tratar `command` como uma sequência de comandos de
        dispositivo. Retorna um resultado combinado se TODOS os pedaços
        validarem como device_action, ou None se não for um comando
        composto reconhecível (aí o chamador segue com o caminho normal
        de intent único, sem nenhuma mudança de comportamento)."""

        parts = [p.strip() for p in _COMPOUND_SPLIT_RE.split(command) if p.strip()]
        if len(parts) < 2:
            return None

        intents = []
        for part in parts:
            intent = self._resolve_device_action(part, person)
            if not intent:
                return None
            intents.append(intent)

        results = []
        for intent in intents:
            if intent.get("entity_id"):
                memory.remember(person, "last_entity_id", intent["entity_id"])
            results.append(intent_router.route(intent))

        memory.remember(person, "last_command", command)
        memory.remember(person, "last_intent", "device_action")

        return {
            "success": all(r.get("success") for r in results),
            "message": " ".join(r.get("message", "").strip() for r in results if r.get("message")),
            "compound": True,
            "steps": results,
        }

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
            # Comando composto (Fase 7)
            # -----------------------------

            compound_result = self._try_compound(command, person)
            if compound_result is not None:
                intent_type = "device_action"
                result = compound_result
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
