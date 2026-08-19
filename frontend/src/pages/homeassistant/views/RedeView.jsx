import { useEffect, useState } from "react";
import { Grid } from "@mui/material";
import NetworkStatusList from "../widgets/NetworkStatusList";
import PacketLossCard from "../../../components/dashboard/PacketLossCard";
import api from "../../../services/api";

// Antes essa view lia entidades do HA (binary_sensor.roteador_*, sensor.cbos_mikrotik_*
// etc, espelho do fred_dashboard.yaml). Desde que o HA Core foi desligado
// (ver memória casa-bruno-ha-removal-phases-4-6), essas entidades pararam de
// existir e tudo aqui ficava preso em Offline/"—" pra sempre. Agora bate
// direto nas fontes reais: ping (routers_service via /network/routers),
// API do RouterOS (/network/mikrotik-status) e ADB (/network/adb) — todas
// rotas públicas de propósito, igual /network/packet-loss, porque essa
// página (Início) não exige login.
//
// Não confundir com pages/Network.jsx (mesmo ping, mas na Gerência, com
// mais detalhe/latência) nem pages/Mikrotik.jsx (interfaces/leases
// completos, também só na Gerência).
const REFRESH_MS = 15000;

export default function RedeView() {

    const [routers, setRouters] = useState(null);
    const [mikrotik, setMikrotik] = useState(null);
    const [adb, setAdb] = useState(null);

    useEffect(() => {
        let active = true;

        async function load() {
            const [routersRes, mikrotikRes, adbRes] = await Promise.allSettled([
                api.get("/network/routers"),
                api.get("/network/mikrotik-status"),
                api.get("/network/adb"),
            ]);
            if (!active) return;
            if (routersRes.status === "fulfilled") setRouters(routersRes.value.data);
            if (mikrotikRes.status === "fulfilled") setMikrotik(mikrotikRes.value.data);
            if (adbRes.status === "fulfilled") setAdb(adbRes.value.data);
        }

        load();
        const interval = setInterval(load, REFRESH_MS);
        return () => {
            active = false;
            clearInterval(interval);
        };
    }, []);

    const routerItems = routers
        ? routers.map((r) => ({ label: r.name, online: r.online }))
        : [
            { label: "Roteador Principal (MR30G)", loading: true },
            { label: "Roteador Sogra (MR60X)", loading: true },
            { label: "Roteador TV/Stream (MR30G)", loading: true },
        ];

    const mikrotikItems = mikrotik
        ? [
            { label: "CPU MikroTik", value: mikrotik.connected ? `${mikrotik.cpu_load}%` : "offline" },
            { label: "Identidade MikroTik", value: mikrotik.connected ? mikrotik.identity : "offline" },
        ]
        : [
            { label: "CPU MikroTik", loading: true },
            { label: "Identidade MikroTik", loading: true },
        ];

    const adbItems = adb
        ? adb.map((d) => ({ label: `${d.name} (ADB)`, online: d.online }))
        : [
            { label: "Projetor HY320 (ADB)", loading: true },
            { label: "BTV13 (ADB)", loading: true },
        ];

    return (
        <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="Roteadores" items={routerItems} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="MikroTik" items={mikrotikItems} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <NetworkStatusList title="Dispositivos Android (ADB)" items={adbItems} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <PacketLossCard />
            </Grid>
        </Grid>
    );
}
