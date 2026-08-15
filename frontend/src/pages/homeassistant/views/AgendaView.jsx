import { useEffect, useState } from "react";
import { Alert, Box, Button, Card, CircularProgress, Stack, TextField, Typography } from "@mui/material";
import EventIcon from "@mui/icons-material/Event";

import api from "../../../services/api";
import SectionLabel from "../../../components/dashboard/SectionLabel";

function formatEventTime(event) {
    const raw = event.start?.dateTime || event.start?.date;
    if (!raw) return "";
    const date = new Date(raw);
    return event.start?.dateTime
        ? date.toLocaleString("pt-BR")
        : date.toLocaleDateString("pt-BR");
}

export default function AgendaView() {

    const [status, setStatus] = useState(null);
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [connecting, setConnecting] = useState(false);
    const [form, setForm] = useState({ summary: "", start: "", end: "" });
    const [createError, setCreateError] = useState("");

    useEffect(() => {

        api.get("/google/calendar/status")
            .then((res) => setStatus(res.data))
            .catch(() => setStatus({ configured: false, connected: false }))
            .finally(() => setLoading(false));

    }, []);

    useEffect(() => {

        if (!status?.connected) return;

        api.get("/google/calendar/events")
            .then((res) => setEvents(res.data || []))
            .catch(() => setEvents([]));

    }, [status]);

    async function handleConnect() {
        setConnecting(true);
        try {
            const res = await api.get("/google/calendar/auth-url");
            window.location.href = res.data.url;
        } catch {
            setConnecting(false);
        }
    }

    async function handleCreate(e) {
        e.preventDefault();
        setCreateError("");
        try {
            await api.post("/google/calendar/events", form);
            setForm({ summary: "", start: "", end: "" });
            const res = await api.get("/google/calendar/events");
            setEvents(res.data || []);
        } catch {
            setCreateError("Não foi possível criar o evento.");
        }
    }

    if (loading) return <CircularProgress />;

    if (!status?.configured) {
        return (
            <Alert severity="info">
                Google Agenda ainda não configurado. Cadastre as credenciais OAuth em
                Gerência → Configurações → Google Agenda.
            </Alert>
        );
    }

    if (!status?.connected) {
        return (
            <Card sx={{ p: 3, textAlign: "center" }}>
                <EventIcon sx={{ fontSize: 40, color: "text.secondary", mb: 1 }} />
                <Typography sx={{ mb: 2 }}>
                    Conecte sua conta do Google para ver e criar eventos por aqui.
                </Typography>
                <Button variant="contained" onClick={handleConnect} disabled={connecting}>
                    {connecting ? "Redirecionando..." : "Conectar Google Agenda"}
                </Button>
            </Card>
        );
    }

    return (
        <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap", alignItems: "flex-start" }}>

            <Card sx={{ p: 2, flex: "2 1 340px" }}>
                <SectionLabel color="info">
                    Próximos eventos
                </SectionLabel>

                {events.length === 0 && (
                    <Typography variant="body2" color="text.secondary">
                        Nenhum evento próximo.
                    </Typography>
                )}

                <Stack spacing={1.5}>
                    {events.map((event) => (
                        <Box key={event.id} sx={{ borderLeft: "3px solid", borderColor: "primary.main", pl: 1.5 }}>
                            <Typography sx={{ fontWeight: 600, whiteSpace: "normal", wordBreak: "break-word" }}>
                                {event.summary || "(sem título)"}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {formatEventTime(event)}
                            </Typography>
                        </Box>
                    ))}
                </Stack>
            </Card>

            <Card component="form" onSubmit={handleCreate} sx={{ p: 2, flex: "1 1 260px" }}>
                <SectionLabel color="secondary">
                    Novo evento
                </SectionLabel>

                <Stack spacing={2}>
                    <TextField
                        label="Título"
                        size="small"
                        required
                        value={form.summary}
                        onChange={(e) => setForm({ ...form, summary: e.target.value })}
                    />
                    <TextField
                        label="Início"
                        type="datetime-local"
                        size="small"
                        required
                        InputLabelProps={{ shrink: true }}
                        value={form.start}
                        onChange={(e) => setForm({ ...form, start: e.target.value })}
                    />
                    <TextField
                        label="Fim"
                        type="datetime-local"
                        size="small"
                        required
                        InputLabelProps={{ shrink: true }}
                        value={form.end}
                        onChange={(e) => setForm({ ...form, end: e.target.value })}
                    />

                    {createError && <Alert severity="error">{createError}</Alert>}

                    <Button type="submit" variant="contained">
                        Criar evento
                    </Button>
                </Stack>
            </Card>

        </Box>
    );
}
