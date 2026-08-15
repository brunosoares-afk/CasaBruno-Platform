import { Card, Grid, Switch, Typography, Box } from "@mui/material";
import SectionLabel from "../../../components/dashboard/SectionLabel";
import PersonIcon from "@mui/icons-material/Person";
import SensorsIcon from "@mui/icons-material/Sensors";
import PowerIcon from "@mui/icons-material/Power";
import TvIcon from "@mui/icons-material/Tv";
import ToggleOnIcon from "@mui/icons-material/ToggleOn";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import { useHomeAssistantStates, useHaServiceCall, indexStates } from "../../../modules/jarvis/services/haApi";

const DOMAIN_ICON = {
    person: PersonIcon,
    sensor: SensorsIcon,
    switch: PowerIcon,
    light: PowerIcon,
    media_player: TvIcon,
    binary_sensor: ToggleOnIcon,
    automation: SmartToyIcon,
};

function isActive(entity, domain) {
    if (!entity) return false;
    if (domain === "person") return entity.state === "home";
    if (["switch", "light", "binary_sensor", "automation"].includes(domain)) return entity.state === "on";
    if (domain === "media_player") return !["off", "idle", "unavailable"].includes(entity.state);
    return false;
}

// entities: [{ entityId, label, showAttribute? }]
// showAttribute mostra attributes[showAttribute] (formatado como data) em
// vez do estado bruto — usado pro "último disparo" das automações.
export default function EntitiesStatusCard({ title, entities, color = "info" }) {

    const { data: states } = useHomeAssistantStates();
    const statesMap = indexStates(states);
    const { mutate: callService } = useHaServiceCall();

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color={color}>
                {title}
            </SectionLabel>

            <Grid container spacing={1.5}>
                {entities.map(({ entityId, label, showAttribute }) => {
                    const entity = statesMap[entityId];
                    const domain = entityId.split(".")[0];
                    const toggleable = domain === "switch" || domain === "light" || domain === "automation";
                    const active = isActive(entity, domain);
                    const Icon = DOMAIN_ICON[domain] || SensorsIcon;
                    // Sem label explícito (ex: vindo da aba Áreas, entidades
                    // descobertas dinamicamente) usa o friendly_name do HA.
                    const displayLabel = label || entity?.attributes?.friendly_name || entityId;

                    let secondary = "—";
                    if (entity) {
                        if (showAttribute) {
                            const value = entity.attributes?.[showAttribute];
                            secondary = value ? new Date(value).toLocaleString("pt-BR") : "Nunca";
                        } else {
                            const unit = entity.attributes?.unit_of_measurement;
                            secondary = unit ? `${entity.state} ${unit}` : entity.state;
                        }
                    }

                    return (
                        <Grid key={entityId} size={{ xs: 12, sm: 6 }}>
                            <Box
                                sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 1.5,
                                    p: 1.5,
                                    borderRadius: 3,
                                    border: "1px solid rgba(255,255,255,.08)",
                                    background: active
                                        ? "linear-gradient(160deg, rgba(0,200,83,.14), rgba(21,101,255,.06))"
                                        : "rgba(255,255,255,.02)",
                                    transition: "background .3s ease, border-color .3s ease",
                                }}
                            >
                                <Box
                                    sx={{
                                        width: 40,
                                        height: 40,
                                        borderRadius: "50%",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        color: "#fff",
                                        flexShrink: 0,
                                        background: active
                                            ? "linear-gradient(135deg, #00C853, #1565FF)"
                                            : "rgba(255,255,255,.08)",
                                    }}
                                >
                                    <Icon fontSize="small" />
                                </Box>

                                <Box sx={{ minWidth: 0, flex: 1 }}>
                                    <Typography variant="body2" fontWeight={600}>
                                        {displayLabel}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        {secondary}
                                    </Typography>
                                </Box>

                                {toggleable ? (
                                    <Switch
                                        checked={entity?.state === "on"}
                                        onChange={() =>
                                            callService({
                                                domain,
                                                service: entity?.state === "on" ? "turn_off" : "turn_on",
                                                entityId,
                                            })
                                        }
                                    />
                                ) : (
                                    <Box
                                        sx={{
                                            width: 8,
                                            height: 8,
                                            borderRadius: "50%",
                                            flexShrink: 0,
                                            bgcolor: active ? "success.main" : "rgba(255,255,255,.2)",
                                        }}
                                    />
                                )}
                            </Box>
                        </Grid>
                    );
                })}
            </Grid>
        </Card>
    );
}
