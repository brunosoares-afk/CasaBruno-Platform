import { useEffect, useState } from "react";
import { Box, Card, Chip, Typography } from "@mui/material";
import api from "../../services/api";
import SectionLabel from "./SectionLabel";

// GET /network/packet-loss é público de propósito (ver app/routers/network.py)
// — esse card aparece tanto no Principal (sem login) quanto na Gerência.
function lossColor(pct) {
    if (pct == null) return "default";
    if (pct < 1) return "success";
    if (pct <= 5) return "warning";
    return "error";
}

export default function PacketLossCard() {

    const [data, setData] = useState(null);

    useEffect(() => {

        let active = true;

        async function load() {
            try {
                const res = await api.get("/network/packet-loss");
                if (active) setData(res.data);
            } catch {
                // silencioso — card só não atualiza nesse ciclo
            }
        }

        load();
        const interval = setInterval(load, 15000);

        return () => {
            active = false;
            clearInterval(interval);
        };

    }, []);

    const pct = data?.loss_percent;

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color="info">
                Perda de Pacotes (Google)
            </SectionLabel>

            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    {data?.target || "8.8.8.8"}
                </Typography>

                <Chip
                    size="small"
                    label={pct == null ? "Coletando..." : `${pct}%`}
                    color={lossColor(pct)}
                />
            </Box>
        </Card>
    );
}
