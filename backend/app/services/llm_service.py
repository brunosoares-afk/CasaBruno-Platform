import logging

import requests

from app.config.settings import settings
from app.services import gemini_service, memory_service
from app.services.expressions import pick
from app.services.homeassistant_service import get_states

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Você é o FRED, o assistente da Casa Bruno (moram lá Bruno e Taiane), "
    "direto e à vontade, tom de conversa por voz — nunca robótico. "
    "Em papo casual, responda de verdade e devolva a pergunta ou puxe "
    "assunto, criando diálogo de verdade. Em comando ou pergunta objetiva, "
    "vá direto ao ponto.\n\n"
    "Português do Brasil, frases curtas, sem markdown. Se não souber (notícia, "
    "clima, dado em tempo real), diga isso em vez de inventar. Só a sua fala, "
    "uma vez — nunca escreva o que a outra pessoa diria."
)

SUMMARY_SYSTEM_PROMPT = (
    "Você atualiza um perfil curto (3 a 5 frases) sobre uma pessoa da casa, "
    "combinando o resumo anterior com as conversas recentes. Foque em fatos "
    "duráveis: preferências, rotina, assuntos que ela costuma trazer, jeito de ser. "
    "Não inclua saudações nem comandos de dispositivo. Responda só com o novo "
    "resumo em português, direto, sem introduções como 'aqui está'."
)

UNKNOWN_PERSON = "desconhecido"


class LLMService:

    def __init__(self):
        self.url = settings.OLLAMA_URL
        self.model = getattr(settings, "OLLAMA_MODEL", "llama3.2:1b")

    def _house_snapshot(self) -> str:
        # Resumo bem curto de propósito — nessa CPU (sem AVX, ver memória
        # casa-bruno-cpu-no-avx) cada token de prompt custa caro, e listar
        # os 22 switches por nome inflava o prompt pra 700+ tokens sozinho,
        # fazendo até "como está seu dia" estourar timeout. Consultas de
        # status de dispositivo específico já vão pelo caminho rápido
        # (intent_engine), não passam por aqui.
        try:
            entities = get_states()
        except Exception:
            return ""

        people = []
        on = 0
        total = 0

        for entity in entities:
            entity_id = entity.get("entity_id", "")
            domain = entity_id.split(".")[0]
            state = entity.get("state")
            name = entity.get("attributes", {}).get("friendly_name", entity_id)

            if domain == "person" and state in ("home", "not_home"):
                people.append(f"{name} {'em casa' if state == 'home' else 'fora'}")

            elif domain == "switch" and state in ("on", "off"):
                total += 1
                if state == "on":
                    on += 1

        parts = []
        if people:
            parts.append(", ".join(people))
        if total:
            parts.append(f"{on}/{total} interruptores ligados")

        return ". ".join(parts)

    def _generate(self, system: str, prompt: str, timeout: int = 60) -> str:
        # Papo livre passa pro Gemini quando configurado — o modelo local
        # (qwen2.5:1.5b, escolhido só por caber na CPU sem AVX de antes)
        # ignora pergunta/alucina/vaza prompt em conversa aberta (ver
        # [[casa-bruno-voice-quality-2026-08-21]]). Cai pro Ollama local se
        # o Gemini falhar (sem internet, cota, etc.) — nunca some a resposta.
        if gemini_service.is_configured():
            try:
                return gemini_service.generate(system, prompt, timeout=min(timeout, 30))
            except Exception:
                logger.warning("Gemini falhou, caindo pro Ollama local", exc_info=True)

        return self._generate_local(system, prompt, timeout)

    def _generate_local(self, system: str, prompt: str, timeout: int = 60) -> str:
        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "system": system,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "stop": ["\nUsuário", "\nFred:", "\nVocê:", "\nPergunta"]
                },
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    def _knowledge_snippet(self, command: str) -> str:
        # Mesmo motivo de _house_snapshot: orçamento de token curto
        # nessa CPU, por isso limit=2 e sem tentar reformular/resumir.
        try:
            hits = memory_service.search_knowledge(command, limit=2)
        except Exception:
            return ""

        if not hits:
            return ""

        return " ".join(hit["content"] for hit in hits)

    def _build_context(self, person: str, command: str = ""):
        profile = memory_service.get_profile(person)
        recent = memory_service.get_recent_turns(person)

        system = SYSTEM_PROMPT
        if profile.get("summary"):
            system += f"\n\nO que você sabe sobre {person}: {profile['summary']}"

        knowledge = self._knowledge_snippet(command)
        if knowledge:
            system += f"\n\nFatos que você conhece, use se forem relevantes: {knowledge}"

        snapshot = self._house_snapshot()
        if snapshot:
            system += f"\n\nEstado da casa agora: {snapshot}."

        vibe = pick("caracteristicas_fred")
        if vibe:
            system += f"\n\nSeu jeito: {vibe}"

        # últimas 2 trocas como lembrete de contexto, em prosa (não em
        # formato de diálogo) pra não incentivar o modelo a continuar
        # "atuando" como as duas pessoas da conversa.
        last_exchange = [m for role, m in recent if role == "user"][-2:]
        prefix = ""
        if last_exchange:
            topics = "; ".join(f'"{m}"' for m in last_exchange)
            prefix = (
                f"Lembrete: há pouco {person} também falou sobre: {topics}. "
                f"Responda apenas à pergunta de agora, sem repetir isso. "
                f"Pergunta de {person} agora: "
            )

        return system, prefix

    def _summarize(self, person: str, old_summary, recent_turns) -> str:
        dialogue = "\n".join(
            f"{'Usuário' if role == 'user' else 'Fred'}: {message}"
            for role, message in recent_turns
        )
        prompt = (
            f"Resumo anterior sobre {person}: {old_summary or '(nenhum ainda)'}\n\n"
            f"Conversas recentes:\n{dialogue}\n\nNovo resumo:"
        )
        return self._generate(SUMMARY_SYSTEM_PROMPT, prompt, timeout=90)

    def ask(self, prompt: str, person: str = UNKNOWN_PERSON, timeout: int = 60) -> str:
        if not prompt:
            return "Não entendi o que você disse."

        person = person or UNKNOWN_PERSON

        try:
            system, prefix = self._build_context(person, prompt)
        except Exception:
            # Falha ao ler memória não pode impedir de responder —
            # segue sem o contexto de perfil/histórico.
            system, prefix = SYSTEM_PROMPT, ""

        try:
            answer = self._generate(system, f"{prefix}{prompt}", timeout=timeout)
            answer = answer or "Não consegui pensar em uma resposta."
        except requests.exceptions.RequestException:
            return "Não consegui pensar agora, tenta de novo daqui a pouco."

        # Falha ao gravar/atualizar a memória não pode derrubar uma
        # resposta que já foi gerada com sucesso.
        try:
            memory_service.register_turn_and_maybe_summarize(
                person, prompt, answer, self._summarize
            )
        except Exception:
            pass

        return answer


llm_service = LLMService()
