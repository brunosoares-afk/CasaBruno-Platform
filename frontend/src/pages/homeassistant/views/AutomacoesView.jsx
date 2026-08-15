import { Grid } from "@mui/material";
import EntitiesStatusCard from "../widgets/EntitiesStatusCard";
import ActionButtonGrid from "../widgets/ActionButtonGrid";

const AUTOMACOES = [
    { entityId: "automation.presenca_chegada_em_casa_liga_a_luz", label: "Presença: Chegada em Casa Liga a Luz", showAttribute: "last_triggered" },
    { entityId: "automation.presenca_chegada_por_reconhecimento_facial", label: "Presença: Chegada por Reconhecimento Facial", showAttribute: "last_triggered" },
    { entityId: "automation.seguranca_rosto_desconhecido_com_casa_vazia", label: "Segurança: Rosto Desconhecido com Casa Vazia", showAttribute: "last_triggered" },
    { entityId: "automation.rotina_bom_dia_por_reconhecimento_facial", label: "Rotina: Bom Dia por Reconhecimento Facial", showAttribute: "last_triggered" },
    { entityId: "automation.rotina_alexa_pergunta_sobre_o_dia_da_taiane", label: "Rotina: Alexa Pergunta sobre o Dia da Taiane", showAttribute: "last_triggered" },
    { entityId: "automation.portao_abre_ao_reconhecer_placa_ovi8d97", label: "Portão: Abre ao Reconhecer Placa OVI8D97", showAttribute: "last_triggered" },
    { entityId: "automation.btv13_perdeu_conexao_adb", label: "BTV13: Perdeu Conexão ADB", showAttribute: "last_triggered" },
    { entityId: "automation.saude_batimento_cardiaco_elevado", label: "Saúde: Batimento Cardíaco Elevado", showAttribute: "last_triggered" },
    { entityId: "automation.reset_bom_dia_diario", label: "Reset: Bom Dia Diário", showAttribute: "last_triggered" },
    { entityId: "automation.reset_conversa_com_taiane_diaria", label: "Reset: Conversa com Taiane Diária", showAttribute: "last_triggered" },
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
