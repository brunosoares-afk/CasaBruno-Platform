import { Grid } from "@mui/material";
import ActionButtonGrid from "../widgets/ActionButtonGrid";

// O card "Automações Ativas" que ficava aqui (EntitiesStatusCard sobre
// automation.* do HA) foi removido 2026-08-19 — eram entidades mortas
// desde o desligamento do HA Core (ver [[casa-bruno-ha-removal-phases-4-6]]),
// por isso o toggle nunca funcionava de verdade. A lista real e com toggle
// funcional (AutomationsCard, GET/POST /automations) mudou pra aba Cenas,
// ao lado de "Atividades" — ver CenasView.jsx.
const EXECUTAR_AGORA = [
    { label: "Modo Cinema", domain: "script", service: "turn_on", entityId: "script.cena_modo_cinema" },
    { label: "Fim de Cinema", domain: "script", service: "turn_on", entityId: "script.cena_fim_de_cinema" },
    { label: "Assistir TV", domain: "script", service: "turn_on", entityId: "script.cena_assistir_tv" },
    { label: "Modo BTV13", domain: "script", service: "turn_on", entityId: "script.cena_modo_btv13" },
    { label: "Bom Dia", domain: "script", service: "turn_on", entityId: "script.cena_bom_dia" },
    { label: "Boa Noite", domain: "script", service: "turn_on", entityId: "script.cena_boa_noite" },
    { label: "Saída de Casa", domain: "script", service: "turn_on", entityId: "script.cena_saida_de_casa" },
    { label: "Chegada em Casa", domain: "automation", service: "trigger", entityId: "automation.presenca_chegada_em_casa_liga_a_luz" },
    { label: "Conforto (Ar)", domain: "script", service: "turn_on", entityId: "script.cena_conforto_ar" },
    { label: "Não Perturbe", domain: "script", service: "turn_on", entityId: "script.cena_nao_perturbe" },
    { label: "Silêncio Total", domain: "script", service: "turn_on", entityId: "script.cena_silencio_total" },
];

export default function AutomacoesView() {

    return (
        <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
                <ActionButtonGrid title="Executar Agora" actions={EXECUTAR_AGORA} columns={3} />
            </Grid>
        </Grid>
    );
}
