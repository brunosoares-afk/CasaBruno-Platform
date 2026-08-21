# area_registry/entity_registry/device_registry só existiam via WebSocket
# da HA (confirmado bem antes: /api/config/area_registry via REST dava
# 404) — não tinha como fazer isso com o HomeAssistantClient (REST) já
# existente. Desde que a HA foi desligada de vez (Fase 10 da remoção,
# 2026-08-16), essa fonte não existe mais e não vai voltar. A divisão por
# cômodo nunca foi replicada em outro lugar (é metadado puro, não estado
# — nada "roda" isso, só agrupa pra exibição), então virou uma lista
# estática própria em vez de tentar reconstruir via WS morto. Atualize
# aqui à mão se um cômodo/dispositivo mudar — baixo trânsito, não
# justifica reconstruir a descoberta automática só pra isso.
# Nome amigável fixo por entidade — a HA fornecia isso via friendly_name
# de estado ao vivo; pra Garagem/Cozinha (ainda geridas pelo Tuya, ver
# [[casa-bruno-migracao-ha-roadmap]] Fase 2) isso nem faria falta, mas pra
# Sala de estar (media_player/switch geridos só pela HA, que não existe
# mais) é a única fonte de nome que sobrou — sem isso o dashboard mostrava
# o entity_id cru. Sempre preenchido, mesmo pra entidade ainda viva, pra
# não ter dois caminhos de exibição diferentes dependendo se a HA
# existia ou não quando esse dado foi escrito.
ENTITY_LABELS = {
    "switch.portao_casa_switch_1": "Portão",
    "switch.lampada_cozinha_switch_1": "Lâmpada Cozinha",
    "media_player.alexa_taiane": "Alexa Taiane",
    "media_player.bruno_s_n65b": "Bruno's N65B",
    "switch.alexa_taiane_do_not_disturb": "Alexa Taiane – Não Perturbe",
    "switch.bruno_s_n65b_do_not_disturb": "Bruno's N65B – Não Perturbe",
}

AREAS = [
    {
        "area_id": "garagem",
        "name": "Garagem",
        "entity_ids": ["switch.portao_casa_switch_1"],
    },
    {
        "area_id": "cozinha",
        "name": "Cozinha",
        "entity_ids": ["switch.lampada_cozinha_switch_1"],
    },
]

# "Sala de estar" (media_player.alexa_taiane/bruno_s_n65b + DND) foi
# removida daqui 2026-08-21 — os mesmos dispositivos já aparecem no
# card "Status Geral" (Equipamentos e Início), esse cômodo virou
# redundante.


class HomeAssistantRegistry:

    def areas_with_entities(self, force=False):
        return [
            {
                **area,
                "entities": [
                    {"entity_id": eid, "label": ENTITY_LABELS.get(eid)}
                    for eid in area["entity_ids"]
                ],
            }
            for area in AREAS
        ]


registry = HomeAssistantRegistry()
