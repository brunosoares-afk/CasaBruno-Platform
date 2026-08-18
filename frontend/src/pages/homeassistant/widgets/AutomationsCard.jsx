import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, Grid, Switch, Typography, Box } from "@mui/material";
import SectionLabel from "../../../components/dashboard/SectionLabel";
import api from "../../../services/api";

async function fetchAutomations() {
    const res = await api.get("/automations");
    return res.data;
}

async function toggleAutomation({ key, enabled }) {
    const res = await api.post(`/automations/${key}`, { enabled });
    return res.data;
}

export default function AutomationsCard({ title = "Atividades", color = "info" }) {

    const queryClient = useQueryClient();

    const { data: allAutomations = [] } = useQuery({
        queryKey: ["automations"],
        queryFn: fetchAutomations,
        refetchInterval: 15000,
    });

    const automations = allAutomations.filter((a) => a.enabled);

    const { mutate: setEnabled, isPending } = useMutation({
        mutationFn: toggleAutomation,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["automations"] }),
    });

    return (
        <Card sx={{ p: 2 }}>
            <SectionLabel color={color}>
                {title}
            </SectionLabel>

            <Grid container spacing={1.5}>
                {automations.map(({ key, label, description, enabled }) => (
                    <Grid key={key} size={{ xs: 12, sm: 6 }}>
                        <Box
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1.5,
                                p: 1.5,
                                borderRadius: 3,
                                border: "1px solid rgba(255,255,255,.08)",
                                background: enabled
                                    ? "linear-gradient(160deg, rgba(0,200,83,.14), rgba(21,101,255,.06))"
                                    : "rgba(255,255,255,.02)",
                                transition: "background .3s ease, border-color .3s ease",
                            }}
                        >
                            <Box sx={{ minWidth: 0, flex: 1 }}>
                                <Typography variant="body2" fontWeight={600}>
                                    {label}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {description}
                                </Typography>
                            </Box>

                            <Switch
                                checked={enabled}
                                disabled={isPending}
                                onChange={(e) => setEnabled({ key, enabled: e.target.checked })}
                            />
                        </Box>
                    </Grid>
                ))}
            </Grid>
        </Card>
    );
}
