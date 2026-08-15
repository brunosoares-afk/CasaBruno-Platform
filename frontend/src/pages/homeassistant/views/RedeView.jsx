import { Grid } from "@mui/material";
import NetworkStatusList from "../widgets/NetworkStatusList";
import PacketLossCard from "../../../components/dashboard/PacketLossCard";

// Espelho leve das entidades de rede do HA (igual ao fred_dashboard.yaml).
// Não confundir com pages/Network.jsx (ping) ou pages/Mikrotik.jsx (API real
// do RouterOS) — são dados diferentes, esta view só bate com o painel do HA.
const ROTEADORES = [
    { entityId: "binary_sensor.roteador_principal_mr30g", label: "Roteador Principal (MR30G)" },
    { entityId: "binary_sensor.roteador_sogra_mr60x", label: "Roteador Sogra (MR60X)" },
    { entityId: "binary_sensor.roteador_tv_stream_mr30g", label: "Roteador TV/Stream (MR30G)" },
];

const MIKROTIK = [
    { entityId: "sensor.cbos_mikrotik_cpu", label: "CPU MikroTik" },
    { entityId: "sensor.cbos_mikrotik_identity", label: "Identidade MikroTik" },
];

const ADB = [
    { entityId: "binary_sensor.projetor_hy320_adb", label: "Projetor HY320 (ADB)" },
    { entityId: "binary_sensor.btv13_adb", label: "BTV13 (ADB)" },
];

export default function RedeView() {

    return (
        <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="Roteadores" entities={ROTEADORES} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="MikroTik" entities={MIKROTIK} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="Dispositivos Android (ADB)" entities={ADB} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <PacketLossCard />
            </Grid>
        </Grid>
    );
}
