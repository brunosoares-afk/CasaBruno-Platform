import { useEffect, useState } from "react";
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    IconButton,
    Stack,
    TextField,
    Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EventNoteIcon from "@mui/icons-material/EventNote";

import api from "../../services/api";
import SectionLabel from "../../components/dashboard/SectionLabel";

const EMPTY_FORM = { date: "", name: "", description: "" };

function formatDate(dateStr) {
    const d = new Date(`${dateStr}T00:00:00`);
    if (Number.isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("pt-BR");
}

export default function RemindersSection() {

    const [reminders, setReminders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState(EMPTY_FORM);
    const [error, setError] = useState("");

    function load() {
        api.get("/reminders")
            .then((res) => setReminders(res.data.items || []))
            .catch(() => setError("Não foi possível carregar os lembretes."))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    async function handleCreate(e) {
        e.preventDefault();
        setError("");
        try {
            await api.post("/reminders", form);
            setForm(EMPTY_FORM);
            load();
        } catch {
            setError("Não foi possível salvar o lembrete.");
        }
    }

    async function handleDelete(id) {
        try {
            await api.delete(`/reminders/${id}`);
            setReminders((prev) => prev.filter((r) => r.id !== id));
        } catch {
            setError("Não foi possível remover o lembrete.");
        }
    }

    if (loading) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="warning">
                    Lembretes
                </SectionLabel>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    No dia cadastrado, o Fred avisa por WhatsApp (texto + voz).
                </Typography>

                <Stack spacing={1.5} sx={{ mb: 3 }}>
                    {reminders.length === 0 && (
                        <Typography variant="body2" color="text.secondary">
                            Nenhum lembrete cadastrado.
                        </Typography>
                    )}

                    {reminders.map((r) => (
                        <Box
                            key={r.id}
                            sx={{
                                display: "flex",
                                alignItems: "flex-start",
                                gap: 1.5,
                                borderLeft: "3px solid",
                                borderColor: r.notified ? "text.secondary" : "primary.main",
                                pl: 1.5,
                                py: 0.5,
                            }}
                        >
                            <EventNoteIcon fontSize="small" sx={{ color: "text.secondary", mt: 0.5 }} />
                            <Box sx={{ flex: 1, minWidth: 0 }}>
                                <Typography sx={{ fontWeight: 600 }}>
                                    {formatDate(r.date)} — {r.name}
                                </Typography>
                                {r.description && (
                                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: "normal", wordBreak: "break-word" }}>
                                        {r.description}
                                    </Typography>
                                )}
                            </Box>
                            <IconButton size="small" onClick={() => handleDelete(r.id)}>
                                <DeleteIcon fontSize="small" />
                            </IconButton>
                        </Box>
                    ))}
                </Stack>

                <Box component="form" onSubmit={handleCreate}>
                    <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap alignItems="flex-start">
                        <TextField
                            label="Data"
                            type="date"
                            size="small"
                            required
                            InputLabelProps={{ shrink: true }}
                            value={form.date}
                            onChange={(e) => setForm({ ...form, date: e.target.value })}
                        />
                        <TextField
                            label="Nome"
                            size="small"
                            required
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            sx={{ flex: "1 1 200px" }}
                        />
                        <TextField
                            label="Descrição"
                            size="small"
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            sx={{ flex: "2 1 260px" }}
                        />
                        <Button type="submit" variant="contained">
                            Adicionar
                        </Button>
                    </Stack>
                </Box>

                {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            </CardContent>
        </Card>
    );
}
