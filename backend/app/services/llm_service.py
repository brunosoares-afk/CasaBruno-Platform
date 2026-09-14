import json
import logging

from app.services import casa_finance_service, crm_mcp_client, gemini_service, memory_service
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

CRM_SYSTEM_PROMPT_EXTRA = (
    "\n\nVocê também tem acesso a um CRM (ferramentas de contato/tarefa/negociação). "
    "Use quando fizer sentido de verdade — Bruno comentar sobre um cliente/lead novo, "
    "pedir pra anotar algo sobre um contato, ou perguntar sobre follow-ups pendentes. "
    "Procure o contato (find_contact) antes de criar um novo, pra não duplicar. "
    "Não force o uso disso em papo que não tem nada a ver com clientes/negócio."
)

FINANCE_SYSTEM_PROMPT_EXTRA = (
    "\n\nVocê também pode registrar gastos e recebimentos na planilha financeira "
    "da casa, quando a pessoa comentar isso numa frase solta (ex: 'gastei 50 no "
    "mercado', 'recebi 200 de salário', 'paguei 30 de uber no pix'). Extraia valor, "
    "tipo (entrada/saída) e uma descrição curta; categoria e meio de pagamento só "
    "se der pra inferir com confiança — não force. Depois de registrar, confirme "
    "rapidinho o que foi anotado (valor e descrição). Só use isso se a frase for "
    "claramente sobre dinheiro entrando ou saindo, nunca chute um registro."
)

GREETING_SYSTEM_PROMPT = (
    "Você é o FRED, o assistente da Casa Bruno. Você acabou de reconhecer "
    "visualmente uma pessoa chegando perto da câmera. Cumprimente ela de "
    "forma natural e breve (1 ou 2 frases curtas), como quem já a conhece — "
    "sem soar como se estivesse lendo um resumo de perfil, sem mencionar "
    "'reconhecimento facial'/'câmera'/'perfil'. Português do Brasil, tom de "
    "voz casual. Só a sua fala, direto, sem introduções."
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
        # 100% Gemini — sem fallback pro Ollama local (ver
        # [[casa-bruno-voice-quality-2026-08-21]] pro motivo original da
        # migração). Se o Gemini falhar, propaga o erro pra quem chamou
        # decidir a mensagem de fallback, em vez de responder pior.
        return gemini_service.generate(system, prompt, timeout=min(timeout, 30))

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

    def greet(self, person: str) -> str:
        """Saudação personalizada pro reconhecimento facial pela câmera web
        (ver [[casa-bruno-profile-aware-greeting-2026-08-23]]) — usa o
        mesmo perfil/resumo de _build_context, mas não loga isso como uma
        'fala' da pessoa (não é uma pergunta dela, é o Fred puxando papo
        sozinho ao reconhecê-la) e não conta pro turn_count/resumo."""
        profile = memory_service.get_profile(person)

        system = GREETING_SYSTEM_PROMPT
        if profile.get("summary"):
            system += f"\n\nO que você sabe sobre {person}: {profile['summary']}"
        else:
            system += f"\n\nVocê ainda não conhece muito sobre {person} além do nome — não invente detalhes."

        try:
            text = self._generate(system, f"Cumprimente {person}, que acabou de chegar.", timeout=20)
            return text.strip() or f"Olá {person}! Tudo bem? Em que posso ser útil?"
        except Exception:
            logger.warning("Falha ao gerar saudação personalizada pra %s", person, exc_info=True)
            return f"Olá {person}! Tudo bem? Em que posso ser útil?"

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

        # CRM e Finanças só entram no papo livre (não em greet/summarize, que
        # são tarefas internas específicas) — e cada um só se o serviço dele
        # realmente respondeu, pra nunca travar/piorar uma resposta por causa
        # de um serviço externo.
        crm_disponivel = False
        try:
            crm_disponivel = crm_mcp_client.disponivel()
        except Exception:
            logger.warning("Checagem de disponibilidade do CRM falhou", exc_info=True)

        finance_disponivel = False
        try:
            finance_disponivel = casa_finance_service.disponivel()
        except Exception:
            logger.warning("Checagem de disponibilidade do Casa (finanças) falhou", exc_info=True)

        tools = []
        system_com_ferramentas = system
        if crm_disponivel:
            tools += crm_mcp_client.declaracoes_para_gemini()
            system_com_ferramentas += CRM_SYSTEM_PROMPT_EXTRA
        if finance_disponivel:
            tools += casa_finance_service.declaracoes_para_gemini()
            system_com_ferramentas += FINANCE_SYSTEM_PROMPT_EXTRA

        # pessoa que está registrando o lançamento (0=Bruno, 1=Taiane, ver
        # PESSOAS em /opt/casa/publico/index.html) — decidido aqui por quem
        # está de fato falando com o Fred no canal, nunca pelo Gemini.
        pessoa_casa = 1 if person == "Taiane" else 0

        def _chamar_ferramenta(nome, argumentos):
            if nome in casa_finance_service.TOOL_NAMES:
                return json.dumps(casa_finance_service.chamar_ferramenta(nome, argumentos, pessoa_casa))
            return crm_mcp_client.chamar_ferramenta(nome, argumentos)

        try:
            if tools:
                answer = gemini_service.generate_with_tools(
                    system_com_ferramentas,
                    f"{prefix}{prompt}",
                    tools,
                    _chamar_ferramenta,
                    timeout=min(timeout, 30),
                )
            else:
                answer = self._generate(system, f"{prefix}{prompt}", timeout=timeout)
            answer = answer or "Não consegui pensar em uma resposta."
        except Exception:
            logger.warning("Gemini falhou em ask()", exc_info=True)
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
