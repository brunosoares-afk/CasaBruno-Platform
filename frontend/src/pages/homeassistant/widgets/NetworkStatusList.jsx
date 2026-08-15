import { Card, Typography, Box, Chip } from "@mui/material";
import RouterIcon from "@mui/icons-material/Router";
import { useHomeAssistantStates, indexStates } from "../../../modules/jarvis/services/haApi";
import SectionLabel from "../../../components/dashboard/SectionLabel";

// Modelo diferente de propósito do EntitiesStatusCard (usado no resto do
// app) — aqui são só leituras de status de rede/infra, sem nada pra
// ligar/desligar, então faz mais sentido como lista tipo "painel de
// monitoramento" (linha com nome + chip/valor) do que os cards com switch.
export default function NetworkStatusList({ title, entities }) {

    const { data: states } = useHomeAssistantStates();
    const statesMap = indexStates(states);

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color="info">
                {title}
            </SectionLabel>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                {entities.map(({ entityId, label }) => {
                    const entity = statesMap[entityId];
                    const domain = entityId.split(".")[0];
                    const isBinary = domain === "binary_sensor";
                    const online = entity?.state === "on";
                    const displayLabel = label || entity?.attributes?.friendly_name || entityId;
                    const unit = entity?.attributes?.unit_of_measurement;
                    const value = entity ? (unit ? `${entity.state} ${unit}` : entity.state) : "—";

                    return (
                        <Box
                            key={entityId}
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
                                    sx={{ color: !entity ? "text.disabled" : isBinary ? (online ? "success.main" : "text.disabled") : "info.main" }}
                                />
                                <Typography variant="body2" sx={{ whiteSpace: "normal", wordBreak: "break-word" }}>
                                    {displayLabel}
                                </Typography>
                            </Box>

                            {isBinary ? (
                                <Chip
                                    size="small"
                                    label={online ? "Online" : "Offline"}
                                    color={online ? "success" : "default"}
                                />
                            ) : (
                                <Typography variant="body2" fontWeight={600} color="info.main" sx={{ whiteSpace: "normal", wordBreak: "break-word" }}>
                                    {value}
                                </Typography>
                            )}
                        </Box>
                    );
                })}
            </Box>
        </Card>
    );
}
