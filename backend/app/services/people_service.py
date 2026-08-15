from app.services.homeassistant_service import get_recognized_person

# Mapa fixo número->nome pro canal WhatsApp (esse número agora é exclusivo
# do Fred, então o remetente É a identidade — diferente da câmera, que só
# reconhece quem passou na frente dela, sem relação com quem está
# mandando a mensagem). Adicione novas pessoas aqui.
PEOPLE_BY_WHATSAPP_JID = {
    "5527996354512@s.whatsapp.net": "Bruno",
    "5527997176739@s.whatsapp.net": "Taiane",
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
