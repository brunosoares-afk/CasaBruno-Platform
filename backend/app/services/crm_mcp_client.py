"""Bridges Fred (synchronous Gemini function-calling loop) to the AgentCRM
MCP server (Node, stdio transport, async-only Python SDK). The MCP session
is spawned once and kept alive in a background thread's event loop — one
tool call per new subprocess would be wasteful and slow.

agentId/agentName are injected here, not left to the model to remember on
every call — any tool whose real MCP schema declares those fields gets them
filled in with Fred's own identity automatically, and they're stripped out
of what Gemini sees so the model never has to think about attribution at
all. See agentcrm's README for why attribution matters: it's what lets a
human audit what an autonomous agent actually did in the CRM.
"""
import asyncio
import logging
import threading

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

AGENTCRM_COMMAND = "node"
AGENTCRM_ARGS = ["/opt/agentcrm/src/mcp/stdio.js"]
FRED_AGENT_ID = "fred"
FRED_AGENT_NAME = "Fred"

# Keys Gemini's function-calling schema doesn't understand (it accepts only
# a restricted OpenAPI-3.0-like subset of JSON Schema) — stripped recursively.
_CHAVES_INCOMPATIVEIS_GEMINI = {"$schema", "additionalProperties"}
_CAMPOS_AGENTE = {"agentId", "agentName"}


def _limpar_schema_para_gemini(schema):
    if not isinstance(schema, dict):
        return schema
    limpo = {}
    for chave, valor in schema.items():
        if chave in _CHAVES_INCOMPATIVEIS_GEMINI:
            continue
        if chave == "type" and isinstance(valor, str):
            # A API do Gemini usa o enum próprio dela (STRING/OBJECT/ARRAY/...
            # maiúsculo), não o "string"/"object" minúsculo do JSON Schema que
            # o zod-to-json-schema do MCP produz — sem isso, 400 Bad Request.
            limpo[chave] = valor.upper()
        elif chave == "properties" and isinstance(valor, dict):
            limpo[chave] = {k: _limpar_schema_para_gemini(v) for k, v in valor.items() if k not in _CAMPOS_AGENTE}
        elif chave == "required" and isinstance(valor, list):
            limpo[chave] = [r for r in valor if r not in _CAMPOS_AGENTE]
        elif chave == "items":
            limpo[chave] = _limpar_schema_para_gemini(valor)
        else:
            limpo[chave] = valor
    return limpo


class _PonteMcp:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True, name="agentcrm-mcp-loop")
        self._thread.start()
        self._session = None
        self._ferramentas = None  # lista bruta de mcp.types.Tool
        self._lock = threading.Lock()
        self._exit_stack = None  # segura stdio_client/ClientSession vivos — sem isso, o GC fecha a conexão assim que _conectar() retorna

    async def _conectar(self):
        from contextlib import AsyncExitStack
        stack = AsyncExitStack()
        params = StdioServerParameters(command=AGENTCRM_COMMAND, args=AGENTCRM_ARGS)
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        resultado = await session.list_tools()
        self._exit_stack = stack
        self._session = session
        self._ferramentas = resultado.tools

    def _rodar(self, coro, timeout=15):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def _garantir_conectado(self):
        with self._lock:
            if self._session is None:
                self._rodar(self._conectar())

    def disponivel(self) -> bool:
        try:
            self._garantir_conectado()
            return self._session is not None
        except Exception:
            logger.warning("AgentCRM MCP indisponível", exc_info=True)
            return False

    def declaracoes_para_gemini(self):
        """Formato FunctionDeclaration do Gemini: name/description/parameters."""
        self._garantir_conectado()
        return [
            {
                "name": t.name,
                "description": t.description or "",
                "parameters": _limpar_schema_para_gemini(t.input_schema),
            }
            for t in self._ferramentas
            # 2026-09-24: o AgentCRM ganhou ferramentas geradas (api_get_*, sqlite_*) pra outros
            # clientes MCP; o Fred continua só com as ferramentas feitas à mão (menos tokens por
            # chamada e sem SQL livre num assistente de voz).
            if not t.name.startswith(("api_get", "api_list", "sqlite_"))
        ]

    def _aceita_campo_agente(self, nome_ferramenta: str, campo: str) -> bool:
        for t in self._ferramentas:
            if t.name == nome_ferramenta:
                return campo in (t.input_schema.get("properties") or {})
        return False

    def chamar(self, nome_ferramenta: str, argumentos: dict) -> str:
        self._garantir_conectado()
        args = dict(argumentos or {})
        if self._aceita_campo_agente(nome_ferramenta, "agentId"):
            args["agentId"] = FRED_AGENT_ID
        if self._aceita_campo_agente(nome_ferramenta, "agentName"):
            args["agentName"] = FRED_AGENT_NAME

        resultado = self._rodar(self._session.call_tool(nome_ferramenta, args))
        textos = [bloco.text for bloco in resultado.content if getattr(bloco, "type", None) == "text"]
        return "\n".join(textos) if textos else "(sem retorno)"


_ponte = _PonteMcp()


def disponivel() -> bool:
    return _ponte.disponivel()


def declaracoes_para_gemini():
    return _ponte.declaracoes_para_gemini()


def chamar_ferramenta(nome: str, argumentos: dict) -> str:
    return _ponte.chamar(nome, argumentos)
