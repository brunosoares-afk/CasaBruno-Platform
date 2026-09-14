"""Ponte entre o tool-calling do Gemini (mesmo mecanismo do crm_mcp_client)
e o webhook de lançamento avulso do app financeiro Casa (/opt/casa,
servidor.js::POST /api/lancamento — o mesmo endpoint que o MacroDroid usa).
Deixa o Fred registrar um gasto/recebimento a partir de uma frase solta em
qualquer canal (WhatsApp, dashboard), sem precisar reescrever nada do Casa.
"""
import logging
import uuid

import requests

from app.config.settings import settings

logger = logging.getLogger(__name__)

REGISTRAR_LANCAMENTO = "registrar_lancamento_financeiro"
TOOL_NAMES = {REGISTRAR_LANCAMENTO}

CATEGORIAS = [
    "Mercado", "Transporte", "Lazer", "Saúde", "Casa", "Contas",
    "Assinaturas", "Restaurante", "Compras", "Salário", "Outros",
]
MEIOS = ["pix", "dinheiro", "cartao_credito", "cartao_debito", "outro"]


def disponivel() -> bool:
    return bool(settings.CASA_API_URL and settings.CASA_TOKEN)


def declaracoes_para_gemini():
    return [
        {
            "name": REGISTRAR_LANCAMENTO,
            "description": (
                "Registra um gasto (saída) ou recebimento (entrada) na planilha "
                "financeira da casa. Use quando a pessoa comentar um gasto ou "
                "recebimento em conversa natural — ex: 'gastei 50 reais no "
                "mercado', 'recebi 200 de salário', 'paguei 30 de uber no pix'."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "valor": {
                        "type": "NUMBER",
                        "description": "Valor em reais, sempre positivo (ex: 50.90)",
                    },
                    "tipo": {
                        "type": "STRING",
                        "enum": ["entrada", "saida"],
                        "description": "'saida' pra gasto, 'entrada' pra recebimento",
                    },
                    "descricao": {
                        "type": "STRING",
                        "description": "Descrição curta do lançamento, ex: 'Mercado', 'Uber', 'Salário'",
                    },
                    "categoria": {
                        "type": "STRING",
                        "enum": CATEGORIAS,
                        "description": "Categoria mais próxima — só preencha se tiver certeza",
                    },
                    "meio": {
                        "type": "STRING",
                        "enum": MEIOS,
                        "description": "Meio de pagamento, só se a pessoa mencionar",
                    },
                },
                "required": ["valor", "tipo", "descricao"],
            },
        }
    ]


def registrar(argumentos: dict, pessoa: int) -> dict:
    """Executa a ferramenta de verdade: chama o webhook do Casa. `pessoa`
    (0=Bruno, 1=Taiane, ver PESSOAS em publico/index.html) vem de quem está
    falando com o Fred no canal (WhatsApp resolve pelo número remetente) —
    não é o Gemini quem decide isso, pra nunca errar o dono do lançamento."""

    valor = argumentos.get("valor")
    tipo = argumentos.get("tipo")
    descricao = argumentos.get("descricao")

    if not valor or tipo not in ("entrada", "saida") or not descricao:
        return {"erro": "faltou valor, tipo (entrada/saida) ou descrição"}

    payload = {
        "valor": valor,
        "tipo": tipo,
        "descricao": str(descricao)[:120],
        "pessoa": pessoa,
        # ref única por chamada — se o Gemini repetir a tool-call (retry de
        # rede, por ex.), o próprio webhook do Casa deduplica por ref.
        "ref": f"fred-{uuid.uuid4().hex[:16]}",
    }
    if argumentos.get("categoria") in CATEGORIAS:
        payload["categoria"] = argumentos["categoria"]
    if argumentos.get("meio") in MEIOS:
        payload["meio"] = argumentos["meio"]

    resp = requests.post(
        f"{settings.CASA_API_URL}/api/lancamento",
        json=payload,
        headers={"x-token": settings.CASA_TOKEN},
        timeout=10,
    )
    resp.raise_for_status()
    dados = resp.json()

    lancamento = dados.get("lancamento") or {}
    return {
        "ok": True,
        "valor": lancamento.get("valor", valor),
        "categoria": lancamento.get("categoria", payload.get("categoria", "Outros")),
        "descricao": lancamento.get("descricao", payload["descricao"]),
    }


def chamar_ferramenta(nome: str, argumentos: dict, pessoa: int) -> dict:
    if nome != REGISTRAR_LANCAMENTO:
        return {"erro": f"ferramenta desconhecida: {nome}"}
    try:
        return registrar(argumentos, pessoa)
    except Exception as e:
        logger.warning("Falha ao registrar lançamento financeiro", exc_info=True)
        return {"erro": str(e)}
