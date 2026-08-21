import { useState } from "react";
import { Stack } from "@mui/material";
import NativeSceneButtons from "../widgets/NativeSceneButtons";
import ActionButtonGrid from "../widgets/ActionButtonGrid";
import AutomationsCard from "../widgets/AutomationsCard";

// Cenas favoritas/fixadas — só localStorage (client-side), sem backend
// pra isso, é pura preferência de exibição de quem está usando o
// navegador.
const PINNED_STORAGE_KEY = "casabruno_cenas_fixadas";

function loadPinned() {
    try {
        const raw = localStorage.getItem(PINNED_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

// Antes chamava script.fred_scene_unitv / script.fred_scene_desenho_heitor
// via HA (script.*) — hoje sabemos que esse entity_id já era interceptado
// local (scenes_service.is_managed, ver homeassistant_service.call_service),
// então funcionaria de qualquer jeito, mas manter a chamada apontando pro
// endpoint nativo em app/routers/scenes.py é mais direto (sem o round-trip
// HA). "UniTV Projetor" (scene.unitv_projetor) foi removida daqui: só
// ligava o projetor sem abrir nada, redundante com "Cena UniTV".
const CENAS = [
    { label: "Cena UniTV", path: "/scenes/unitv" },
    { label: "Cena Desenho Heitor", path: "/scenes/desenho-heitor" },
];

// As 10 "cena_*" de scripts.yaml — só existiam no HA como wrapper fino
// (script -> rest_command -> HTTP -> nosso próprio backend); já estão
// 100% portadas em app/services/scenes_service.py (CENA_LABELS) e
// interceptadas antes de qualquer chamada real ao HA, então continuam
// funcionando disparadas como script.* mesmo com o HA Core desligado.
// Só não estavam nesta tela — moravam soltas em AutomacoesView.jsx.
const OUTRAS_CENAS = [
    { label: "Modo Cinema", domain: "script", service: "turn_on", entityId: "script.cena_modo_cinema" },
    { label: "Fim de Cinema", domain: "script", service: "turn_on", entityId: "script.cena_fim_de_cinema" },
    { label: "Assistir TV", domain: "script", service: "turn_on", entityId: "script.cena_assistir_tv" },
    { label: "Modo BTV13", domain: "script", service: "turn_on", entityId: "script.cena_modo_btv13" },
    { label: "Bom Dia", domain: "script", service: "turn_on", entityId: "script.cena_bom_dia" },
    { label: "Boa Noite", domain: "script", service: "turn_on", entityId: "script.cena_boa_noite" },
    { label: "Saída de Casa", domain: "script", service: "turn_on", entityId: "script.cena_saida_de_casa" },
    { label: "Conforto (Ar)", domain: "script", service: "turn_on", entityId: "script.cena_conforto_ar" },
    { label: "Não Perturbe", domain: "script", service: "turn_on", entityId: "script.cena_nao_perturbe" },
    { label: "Silêncio Total", domain: "script", service: "turn_on", entityId: "script.cena_silencio_total" },
    { label: "Chegando de Carro", domain: "script", service: "turn_on", entityId: "script.cena_chegando_de_carro" },
    { label: "Chegando a Pé", domain: "script", service: "turn_on", entityId: "script.cena_chegando_a_pe" },
    { label: "Portão", domain: "script", service: "turn_on", entityId: "script.cena_portao" },
    { label: "Modo Visita", domain: "script", service: "turn_on", entityId: "script.cena_modo_visita" },
];

export default function CenasView() {
    const [pinned, setPinned] = useState(loadPinned);

    const togglePin = (entityId) => {
        setPinned((prev) => {
            const next = prev.includes(entityId)
                ? prev.filter((id) => id !== entityId)
                : [...prev, entityId];
            localStorage.setItem(PINNED_STORAGE_KEY, JSON.stringify(next));
            return next;
        });
    };

    const favoritas = OUTRAS_CENAS.filter((a) => pinned.includes(a.entityId));

    return (
        <Stack spacing={2}>
            {favoritas.length > 0 && (
                <ActionButtonGrid
                    title="Favoritas"
                    actions={favoritas}
                    columns={3}
                    color="success"
                    pinnedIds={pinned}
                    onTogglePin={togglePin}
                />
            )}
            <NativeSceneButtons title="Cenas T&B Residencial" actions={CENAS} columns={3} />
            <ActionButtonGrid
                title="Outras Cenas"
                actions={OUTRAS_CENAS}
                columns={3}
                color="primary"
                pinnedIds={pinned}
                onTogglePin={togglePin}
            />
            <AutomationsCard title="Atividades" />
            <AutomationsCard title="Automações" onlyEnabled={false} />
        </Stack>
    );
}
