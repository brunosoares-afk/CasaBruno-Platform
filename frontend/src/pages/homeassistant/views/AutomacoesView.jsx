import { Grid } from "@mui/material";
import EntitiesStatusCard from "../widgets/EntitiesStatusCard";
import ActionButtonGrid from "../widgets/ActionButtonGrid";

// As 5 automações de reconhecimento facial/placa (chegada, bom dia,
// conversa com Taiane, rosto desconhecido, placa OVI8D97) foram removidas
// do HA em 2026-08-16 — já estavam mortas desde a Fase 1 da migração
// (trigger era um sensor sintético que só existe no relay do nosso
// backend, sensor.icsee_pessoa_reconhecida, nunca existiu de verdade no
// HA Core) e a lógica real já rodava só em app/services/automations_service.py.
// Ver [[casa-bruno-ha-removal-phases-4-6]].
const AUTOMACOES = [
    { entityId: "automation.presenca_chegada_em_casa_liga_a_luz", label: "Presença: Chegada em Casa Liga a Luz", showAttribute: "last_triggered" },
    { entityId: "automation.btv13_perdeu_conexao_adb", label: "BTV13: Perdeu Conexão ADB", showAttribute: "last_triggered" },
    { entityId: "automation.saude_batimento_cardiaco_elevado", label: "Saúde: Batimento Cardíaco Elevado", showAttribute: "last_triggered" },
];

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
                <EntitiesStatusCard title="Automações Ativas" entities={AUTOMACOES} />
            </Grid>

            <Grid size={{ xs: 12 }}>
                <ActionButtonGrid title="Executar Agora" actions={EXECUTAR_AGORA} columns={3} />
            </Grid>
        </Grid>
    );
}
