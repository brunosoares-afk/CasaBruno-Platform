import { Card, Grid, Box, Typography } from "@mui/material";
import BoltIcon from "@mui/icons-material/Bolt";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import { useHaServiceCall } from "../../../modules/jarvis/services/haApi";
import SectionLabel from "../../../components/dashboard/SectionLabel";

// actions: [{ label, icon?, domain, service, entityId, data? }]
// pinnedIds/onTogglePin são opcionais — só quem quer o "fixar" (ex:
// Cenas) passa; sem eles a estrela nem aparece, resto do app não muda.
export default function ActionButtonGrid({ title, actions, columns = 3, color = "secondary", pinnedIds, onTogglePin }) {

    const { mutate: callService, isPending } = useHaServiceCall();
    const smSize = 12 / columns;

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color={color}>
                {title}
            </SectionLabel>

            <Grid container spacing={1.5}>
                {actions.map((a) => (
                    <Grid key={a.label} size={{ xs: 6, sm: smSize }}>
                        <Box
                            onClick={() =>
                                !isPending &&
                                callService({
                                    domain: a.domain,
                                    service: a.service,
                                    entityId: a.entityId,
                                    data: a.data,
                                })
                            }
                            sx={{
                                position: "relative",
                                cursor: isPending ? "default" : "pointer",
                                p: 2,
                                borderRadius: 3,
                                textAlign: "center",
                                border: "1px solid rgba(255,255,255,.08)",
                                background: "linear-gradient(160deg, rgba(21,101,255,.12), rgba(255,79,216,.07))",
                                transition: "transform .18s ease, box-shadow .18s ease, border-color .18s ease",
                                opacity: isPending ? 0.6 : 1,
                                userSelect: "none",
                                "&:hover": {
                                    transform: "translateY(-3px) scale(1.02)",
                                    boxShadow: "0 14px 28px rgba(21,101,255,.28)",
                                    borderColor: "rgba(21,101,255,.55)",
                                },
                                "&:active": {
                                    transform: "translateY(-1px) scale(0.99)",
                                },
                            }}
                        >
                            {onTogglePin && (
                                <Box
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onTogglePin(a.entityId);
                                    }}
                                    sx={{
                                        position: "absolute",
                                        top: 4,
                                        right: 4,
                                        display: "flex",
                                        color: pinnedIds?.includes(a.entityId) ? "#FFD54F" : "rgba(255,255,255,.35)",
                                        "&:hover": { color: "#FFD54F" },
                                    }}
                                >
                                    {pinnedIds?.includes(a.entityId)
                                        ? <StarIcon fontSize="small" />
                                        : <StarBorderIcon fontSize="small" />}
                                </Box>
                            )}

                            <Box
                                sx={{
                                    width: 44,
                                    height: 44,
                                    mx: "auto",
                                    mb: 1,
                                    borderRadius: "50%",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    color: "#fff",
                                    background: "linear-gradient(135deg, #1565FF, #FF4FD8)",
                                }}
                            >
                                {a.icon || <BoltIcon fontSize="small" />}
                            </Box>

                            <Typography variant="body2" fontWeight={600}>
                                {a.label}
                            </Typography>
                        </Box>
                    </Grid>
                ))}
            </Grid>
        </Card>
    );
}
