import re

import requests

from app.config.settings import settings

USER_AGENT = "CasaBrunoFred/1.0 (home assistant local; contact: n/a)"
TIMEOUT = 5
MAX_SENTENCES = 3


def _trim(text: str, max_sentences: int = MAX_SENTENCES) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:max_sentences]).strip()


def _opensearch_titles(query: str, lang: str) -> list[str]:
    resp = requests.get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={
            "action": "opensearch",
            "search": query,
            "limit": 3,
            "namespace": 0,
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data[1] if len(data) > 1 else []


def _summary(title: str, lang: str) -> str | None:
    resp = requests.get(
        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}",
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    # Página de desambiguação ("Pedro II" -> vários "Pedro II" possíveis)
    # tem um extract genérico e inútil ("X ou Y pode referir-se a:") —
    # melhor pular pro próximo candidato do opensearch do que devolver
    # isso como se fosse a resposta.
    if data.get("type") == "disambiguation":
        return None
    extract = data.get("extract")
    return _trim(extract) if extract else None


def search_wikipedia(query: str, lang: str | None = None) -> str | None:
    """Busca um resumo curto na Wikipedia pública (sem API key). Retorna
    None se nada for encontrado ou a rede falhar — quem chamar decide
    como degradar (ver intent_handlers.knowledge_search)."""

    if not query:
        return None

    lang = lang or settings.WIKIPEDIA_LANG

    try:
        titles = _opensearch_titles(query, lang)
        for title in titles:
            extract = _summary(title, lang)
            if extract:
                return extract
        return None
    except requests.RequestException:
        return None
