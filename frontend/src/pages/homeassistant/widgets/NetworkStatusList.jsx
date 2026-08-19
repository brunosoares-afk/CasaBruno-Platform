import { Card, Typography, Box, Chip } from "@mui/material";
import RouterIcon from "@mui/icons-material/Router";
import SectionLabel from "../../../components/dashboard/SectionLabel";

// Modelo diferente de propósito do EntitiesStatusCard (usado no resto do
// app) — aqui são só leituras de status de rede/infra, sem nada pra
// ligar/desligar, então faz mais sentido como lista tipo "painel de
// monitoramento" (linha com nome + chip/valor) do que os cards com switch.
//
// `items`: [{ label, online?, value?, loading? }] — vem de endpoints
// próprios do backend (/network/*, /mikrotik/*), não mais do HA (ver
// RedeView.jsx pro porquê).
export default function NetworkStatusList({ title, items }) {

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color="info">
                {title}
            </SectionLabel>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                {items.map(({ label, online, value, loading }) => {
                    const isBinary = value === undefined;

                    return (
                        <Box
                            key={label}
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                gap: 1,
                                p: 1.25,
                                borderRadius: 2,
                                border: "1px solid rgba(255,255,255,.06)",
                                background: "rgba(255,255,255,.02)",
                            }}
                        >
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, minWidth: 0 }}>
                                <RouterIcon
                                    fontSize="small"
                                    sx={{ color: loading ? "text.disabled" : isBinary ? (online ? "success.main" : "text.disabled") : "info.main" }}
                                />
                                <Typography variant="body2" sx={{ whiteSpace: "normal", wordBreak: "break-word" }}>
                                    {label}
                                </Typography>
                            </Box>

                            {isBinary ? (
                                <Chip
                                    size="small"
                                    label={loading ? "..." : online ? "Online" : "Offline"}
                                    color={online ? "success" : "default"}
                                />
                            ) : (
                                <Typography variant="body2" fontWeight={600} color="info.main" sx={{ whiteSpace: "normal", wordBreak: "break-word" }}>
                                    {loading ? "—" : value}
                                </Typography>
                            )}
                        </Box>
                    );
                })}
            </Box>
        </Card>
    );
}
