from app.services.homeassistant_service import get_recognized_person

# Mapa fixo número->nome pro canal WhatsApp (esse número agora é exclusivo
# do Fred, então o remetente É a identidade — diferente da câmera, que só
# reconhece quem passou na frente dela, sem relação com quem está
# mandando a mensagem). Adicione novas pessoas aqui.
PEOPLE_BY_WHATSAPP_JID = {
    "5527996354512@s.whatsapp.net": "Bruno",
    # Corrigido 2026-08-16 — o número que estava salvo (...6739) estava
    # errado; confirmado com o Bruno que o certo termina em ...6379.
    "5527997176379@s.whatsapp.net": "Taiane",
    # Mesma pessoa (Bruno), identificador alternativo — o WhatsApp às
    # vezes reporta o remetente por um @lid (Linked ID, ligado a um
    # device vinculado) em vez do JID de telefone, dependendo de qual
    # dispositivo ele usou pra mandar a mensagem. Confirmado nos logs
    # 2026-08-15/16: mesma pessoa mandando "Olá fred", "Sim" e vários
    # áudios, sempre por esse @lid — sem isso, todo esse tráfego caía
    # como remetente "anônimo" e perdia acesso à memória por pessoa
    # (confirmações pendentes, last_entity_id pra pronome, preferências).
    "94038392873044@lid": "Bruno",
}


def resolve_person(channel: str, sender: str | None = None) -> str:
    """Quem está falando com o Fred agora, pro sistema de memória por
    pessoa (Fase 6). WhatsApp tem identidade real via o número que
    mandou a mensagem; voz/web ainda não têm um sinal equivalente, então
    caem no reconhecimento facial da câmera como aproximação (mesmo
    comportamento de antes, não é regressão — só não é mais usado como
    identidade padrão pro WhatsApp)."""

    if channel == "whatsapp" and sender:
        return PEOPLE_BY_WHATSAPP_JID.get(sender, sender)

    return get_recognized_person()


def is_allowed_whatsapp_sender(sender: str) -> bool:
    """Allowlist do canal WhatsApp (2026-08-16, a pedido do Bruno, depois
    de um terceiro desconhecido — @lid não relacionado à casa — ter
    recebido respostas reais do Fred, ver [[casa-bruno-whatsapp-lid-identity-2026-08-16]]).
    Só quem está em PEOPLE_BY_WHATSAPP_JID (Bruno/Taiane, incluindo
    identificadores @lid alternativos já mapeados) passa; qualquer outro
    remetente é ignorado antes de gastar LLM/TTS com ele."""
    return sender in PEOPLE_BY_WHATSAPP_JID
