import json
import random
from pathlib import Path

import requests

from app.config.settings import settings
from app.services import memory_service

EXPRESSIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "fred_expressions.json"

try:
    with open(EXPRESSIONS_PATH, encoding="utf-8") as f:
        EXPRESSIONS = json.load(f)
except Exception:
    EXPRESSIONS = {}

SYSTEM_PROMPT = (
    "Você é o FRED, assistente pessoal da Casa Bruno. Responda em português do Brasil, "
    "de forma direta, específica e natural, como numa conversa por voz pela Alexa. "
    "Nunca dê respostas vagas ou genéricas — vá direto ao ponto da pergunta feita. "
    "Se não souber algo (como notícias, clima ou dados em tempo real), diga isso "
    "claramente em vez de inventar ou enrolar. Frases curtas, sem markdown, sem listas. "
    "Dê APENAS a sua resposta, uma única vez. Nunca escreva falas da outra pessoa "
    "nem invente perguntas ou continue a conversa sozinho."
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

    def _sample_expressions(self, per_category: int = 1) -> str:
        if not EXPRESSIONS:
            return ""
        picked = []
        for category, options in EXPRESSIONS.items():
            if options:
                picked.extend(random.sample(options, min(per_category, len(options))))
        if not picked:
            return ""
        return ", ".join(f'"{p}"' for p in picked)

    def _generate(self, system: str, prompt: str, timeout: int = 60) -> str:
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

    def _build_context(self, person: str):
        profile = memory_service.get_profile(person)
        recent = memory_service.get_recent_turns(person)

        system = SYSTEM_PROMPT
        if profile.get("summary"):
            system += f"\n\nO que você sabe sobre {person}: {profile['summary']}"

        expressions = self._sample_expressions()
        if expressions:
            system += (
                f"\n\nPra soar mais natural, pode se inspirar (sem copiar sempre "
                f"as mesmas) em expressões como: {expressions}."
            )

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
            system, prefix = self._build_context(person)
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
