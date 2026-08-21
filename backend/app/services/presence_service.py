import logging
import re

from app.core.mikrotik.client import mikrotik_client

logger = logging.getLogger("presence_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Mesma ideia do tuya_service.ENTITY_TO_DEVICE: MAC do celular -> entity_id
# que a HA (via mobile_app) já produzia — mesmo entity_id, mesmo shape de
# estado ("home"/"not_home"), pra nenhum consumidor (dashboard, automations_service,
# Fred) precisar mudar. MACs confirmados com o Bruno em 2026-08-16 — cada
# pessoa tinha 2 leases com o mesmo nome de aparelho no MikroTik (troca de
# roteador/rede), a confirmação evitou cravar o MAC errado numa automação
# de segurança (ver [[casa-bruno-migracao-ha-roadmap]] pro histórico da
# tentativa anterior, que ficou pendente por falta dessa confirmação).
MAC_TO_ENTITY = {
    "96:24:6A:C6:E0:14": "person.casa_inteligente",  # Bruno, POCO X8, rede de casa
    "BE:80:F2:F2:CE:2A": "person.taiane",  # Taiane, POCO X6, rede Sogra
    # Segundo MAC do mesmo aparelho (POCO X6) — Android randomiza o MAC
    # por rede, então na rede principal ela aparece com um MAC diferente
    # do da rede Sogra. Confirmado com o Bruno 2026-08-21. Duas entradas
    # pra mesma person.* já funcionam sem mudar get_presence() (agrega
    # "home" se qualquer uma das leases estiver recente).
    "D2:50:EB:51:EF:DB": "person.taiane",  # Taiane, POCO X6, rede principal
    "76:08:46:6B:B9:11": "person.heitor",  # Heitor, Redmi Note 12S, rede principal
}

FRIENDLY_NAME = {
    "person.casa_inteligente": "Casa Inteligente",
    "person.taiane": "Taiane",
    "person.heitor": "Heitor",
}

# Lease "bound" persiste mesmo com o aparelho fora do ar (é uma reserva
# estática, não expira como lease dinâmica) — o "last-seen" do lease
# PARECIA ser o sinal certo (quando o roteador viu tráfego/ARP de
# verdade), mas descoberto 2026-08-21 que isso é falso: "last-seen" só
# atualiza em eventos de protocolo DHCP (renovação), não em tráfego real
# — com lease-time de 12h isso pode ficar horas sem atualizar mesmo com
# o aparelho conectado o tempo todo (Taiane e Heitor confirmados em casa
# mostravam 3h+ de "last-seen" e "Fora" no dashboard). A tabela ARP
# (/ip/arp) reflete presença de verdade — testado ao vivo, os dois
# apareciam lá com status "stale"/complete=true bem antes do lease
# "acordar". Fonte primária agora é ARP; o lease vira só um OR extra
# (não atrapalha, só ajuda no raro caso do ARP não ter a entrada mas o
# DHCP acabou de ver o aparelho).
HOME_THRESHOLD_SECONDS = 1800

_DURATION_RE = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")


def _parse_last_seen(value: str) -> int | None:
    """'2d11h31m34s' -> segundos. RouterOS omite unidades zeradas
    (ex: '34s', '5m57s'), por isso os 4 grupos são opcionais."""
    if not value:
        return None
    m = _DURATION_RE.fullmatch(value.strip())
    if not m or not any(m.groups()):
        return None
    days, hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def get_presence() -> dict[str, str]:
    """entity_id -> 'home'/'not_home' pros MACs conhecidos. Dict vazio se
    o MikroTik não respondeu (chamador decide se mantém o último estado)."""
    try:
        arp_entries = mikrotik_client.arp()
    except Exception:
        logger.exception("Falha ao ler ARP do MikroTik")
        arp_entries = None

    try:
        leases = mikrotik_client.dhcp_leases()
    except Exception:
        logger.exception("Falha ao ler leases do MikroTik")
        leases = None

    if arp_entries is None and leases is None:
        return {}

    result: dict[str, str] = {}

    for entry in arp_entries or []:
        mac = (entry.get("mac-address") or "").upper()
        entity_id = MAC_TO_ENTITY.get(mac)
        if not entity_id:
            continue
        is_home = entry.get("complete") == "true"
        if is_home or entity_id not in result:
            result[entity_id] = "home" if is_home else "not_home"

    for lease in leases or []:
        mac = (lease.get("mac-address") or "").upper()
        entity_id = MAC_TO_ENTITY.get(mac)
        if not entity_id:
            continue

        age = _parse_last_seen(lease.get("last-seen", ""))
        is_home = age is not None and age <= HOME_THRESHOLD_SECONDS

        if is_home:
            result[entity_id] = "home"
        elif entity_id not in result:
            result[entity_id] = "not_home"

    return result
