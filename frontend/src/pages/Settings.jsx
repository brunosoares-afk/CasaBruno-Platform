import { useEffect, useState } from "react";
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Switch,
    FormControlLabel,
    Button,
    IconButton,
    Alert,
    Stack,
    Chip,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import UploadIcon from "@mui/icons-material/Upload";

import api from "../services/api";
import { useJarvis } from "../modules/jarvis/context/JarvisContext";
import VoiceSettingsPanel from "../modules/jarvis/components/VoiceSettingsPanel";
import FloorPlanMarkersEditor from "./settings/FloorPlanMarkersEditor";
import RemindersSection from "./settings/RemindersSection";
import SectionLabel from "../components/dashboard/SectionLabel";

function useConfigSection(section, fallback) {

    const [data, setData] = useState(fallback);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState(null); // {type: "success"|"error", text}

    useEffect(() => {
        api.get(`/api/config/${section}`)
            .then((res) => setData({ ...fallback, ...res.data }))
            .catch(() => setStatus({ type: "error", text: "Não foi possível carregar." }))
            .finally(() => setLoading(false));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [section]);

    async function save(value) {
        try {
            await api.post(`/api/config/${section}`, value);
            setData(value);
            setStatus({ type: "success", text: "Salvo." });
        } catch {
            setStatus({ type: "error", text: "Erro ao salvar." });
        }
    }

    return { data, setData, loading, status, setStatus, save };
}

function HomeAssistantSection() {

    const { data, setData, loading, status, save } = useConfigSection("homeassistant", {
        host: "", port: 8123, ssl: false, token: "",
    });

    if (loading) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="primary">
                    Home Assistant
                </SectionLabel>

                <Stack spacing={2}>
                    <TextField
                        label="Host"
                        value={data.host}
                        onChange={(e) => setData({ ...data, host: e.target.value })}
                    />
                    <TextField
                        label="Porta"
                        type="number"
                        value={data.port}
                        onChange={(e) => setData({ ...data, port: Number(e.target.value) })}
                    />
                    <FormControlLabel
                        control={
                            <Switch
                                checked={data.ssl}
                                onChange={(e) => setData({ ...data, ssl: e.target.checked })}
                            />
                        }
                        label="SSL"
                    />
                    <TextField
                        label="Token (long-lived access token)"
                        type="password"
                        value={data.token}
                        onChange={(e) => setData({ ...data, token: e.target.value })}
                    />

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

function MikrotikSection() {

    const { data, setData, loading, status, save } = useConfigSection("mikrotik", {
        host: "", port: 8728, user: "", password: "",
    });

    if (loading) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="info">
                    MikroTik
                </SectionLabel>

                <Stack spacing={2}>
                    <TextField
                        label="Host"
                        value={data.host}
                        onChange={(e) => setData({ ...data, host: e.target.value })}
                    />
                    <TextField
                        label="Porta"
                        type="number"
                        value={data.port}
                        onChange={(e) => setData({ ...data, port: Number(e.target.value) })}
                    />
                    <TextField
                        label="Usuário"
                        value={data.user}
                        onChange={(e) => setData({ ...data, user: e.target.value })}
                    />
                    <TextField
                        label="Senha"
                        type="password"
                        value={data.password}
                        onChange={(e) => setData({ ...data, password: e.target.value })}
                    />

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

function NetworkDevicesSection() {

    const { data, setData, loading, status, save } = useConfigSection("network_devices", { items: [] });

    if (loading) return null;

    function updateItem(i, field, value) {
        const items = [...data.items];
        items[i] = { ...items[i], [field]: value };
        setData({ ...data, items });
    }

    function removeItem(i) {
        setData({ ...data, items: data.items.filter((_, idx) => idx !== i) });
    }

    function addItem() {
        setData({ ...data, items: [...data.items, { name: "", host: "" }] });
    }

    return (
        <Card sx={{ p: 2 }}>
            <CardContent>
                <SectionLabel color="primary">
                    Dispositivos de Rede Monitorados
                </SectionLabel>

                <Stack spacing={2}>
                    {data.items.map((item, i) => (
                        <Box key={i} sx={{ display: "flex", gap: 1 }}>
                            <TextField
                                label="Nome"
                                value={item.name}
                                onChange={(e) => updateItem(i, "name", e.target.value)}
                                fullWidth
                            />
                            <TextField
                                label="Host"
                                value={item.host}
                                onChange={(e) => updateItem(i, "host", e.target.value)}
                                fullWidth
                            />
                            <IconButton onClick={() => removeItem(i)}>
                                <DeleteIcon />
                            </IconButton>
                        </Box>
                    ))}

                    <Button startIcon={<AddIcon />} onClick={addItem} sx={{ alignSelf: "flex-start" }}>
                        Adicionar dispositivo
                    </Button>

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

function FredSection() {

    const { voice, setVoice, wakeWords, setWakeWords } = useJarvis();
    const [newWord, setNewWord] = useState("");

    function removeWord(i) {
        setWakeWords(wakeWords.filter((_, idx) => idx !== i));
    }

    function addWord() {
        const w = newWord.trim().toLowerCase();
        if (w && !wakeWords.includes(w)) {
            setWakeWords([...wakeWords, w]);
        }
        setNewWord("");
    }

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="secondary">
                    Fred — Voz e Palavra de Ativação
                </SectionLabel>

                <VoiceSettingsPanel open voice={voice} onVoiceChange={setVoice} />

                <Typography variant="body2" color="text.secondary" sx={{ mt: 3, mb: 1 }}>
                    Palavras de ativação (salvam assim que adicionadas/removidas)
                </Typography>

                <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mb: 2 }}>
                    {wakeWords.map((w, i) => (
                        <Chip key={w} label={w} onDelete={() => removeWord(i)} />
                    ))}
                </Stack>

                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    <TextField
                        size="small"
                        label="Nova palavra"
                        value={newWord}
                        onChange={(e) => setNewWord(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                e.preventDefault();
                                addWord();
                            }
                        }}
                    />
                    <Button onClick={addWord}>Adicionar</Button>
                </Box>
            </CardContent>
        </Card>
    );
}

function FloorPlanSection() {

    const [info, setInfo] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");

    function loadInfo() {
        api.get("/api/uploads/floor-plan/info")
            .then((res) => setInfo(res.data))
            .catch(() => setInfo({ exists: false, url: null }));
    }

    useEffect(loadInfo, []);

    async function handleUpload(e) {
        const file = e.target.files?.[0];
        e.target.value = "";
        if (!file) return;

        setUploading(true);
        setError("");
        try {
            const formData = new FormData();
            formData.append("file", file);
            const res = await api.post("/api/uploads/floor-plan", formData);
            setInfo(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || "Não foi possível enviar a imagem.");
        } finally {
            setUploading(false);
        }
    }

    async function handleDelete() {
        try {
            const res = await api.delete("/api/uploads/floor-plan");
            setInfo(res.data);
        } catch {
            setError("Não foi possível remover a imagem.");
        }
    }

    if (!info) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="success">
                    Planta da Casa
                </SectionLabel>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Usada no centro da aba Início do Principal. Aceita PNG, JPG, WEBP ou SVG.
                </Typography>

                {info.exists && (
                    <Box
                        component="img"
                        src={`${api.defaults.baseURL}${info.url}`}
                        alt="Planta da casa"
                        sx={{ maxWidth: "100%", maxHeight: 260, display: "block", mb: 2, borderRadius: 1 }}
                    />
                )}

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                    <Button
                        component="label"
                        variant="contained"
                        startIcon={<UploadIcon />}
                        disabled={uploading}
                    >
                        {uploading ? "Enviando..." : info.exists ? "Trocar imagem" : "Enviar imagem"}
                        <input
                            type="file"
                            accept=".png,.jpg,.jpeg,.webp,.svg"
                            hidden
                            onChange={handleUpload}
                        />
                    </Button>

                    {info.exists && (
                        <Button color="error" startIcon={<DeleteIcon />} onClick={handleDelete}>
                            Remover
                        </Button>
                    )}
                </Stack>

                {info.exists && (
                    <FloorPlanMarkersEditor floorPlanUrl={`${api.defaults.baseURL}${info.url}`} />
                )}
            </CardContent>
        </Card>
    );
}

function GoogleCalendarSection() {

    const { data, setData, loading, status, save } = useConfigSection("google_calendar", {
        client_id: "", client_secret: "", redirect_uri: "",
    });

    if (loading) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="info">
                    Google Agenda
                </SectionLabel>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Credenciais OAuth criadas no Google Cloud Console. Registre a "Redirect URI" abaixo
                    exatamente como cadastrada lá — depois disso, o botão de conectar aparece na aba
                    Agenda do Principal.
                </Typography>

                <Stack spacing={2}>
                    <TextField
                        label="Client ID"
                        value={data.client_id}
                        onChange={(e) => setData({ ...data, client_id: e.target.value })}
                    />
                    <TextField
                        label="Client Secret"
                        type="password"
                        value={data.client_secret}
                        onChange={(e) => setData({ ...data, client_secret: e.target.value })}
                    />
                    <TextField
                        label="Redirect URI"
                        placeholder="https://hda08fx9s7v.sn.mynetname.net/casa/api/google/calendar/callback"
                        value={data.redirect_uri}
                        onChange={(e) => setData({ ...data, redirect_uri: e.target.value })}
                    />

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

function NabuCasaSection() {

    const { data, setData, loading, status, save } = useConfigSection("nabu_casa", {
        amount: "", dueDate: "", notes: "",
    });

    if (loading) return null;

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="error">
                    Fatura Nabu Casa
                </SectionLabel>

                <Stack spacing={2}>
                    <TextField
                        label="Valor"
                        value={data.amount}
                        onChange={(e) => setData({ ...data, amount: e.target.value })}
                    />
                    <TextField
                        label="Vencimento"
                        type="date"
                        value={data.dueDate}
                        onChange={(e) => setData({ ...data, dueDate: e.target.value })}
                        InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                        label="Observações"
                        multiline
                        minRows={2}
                        value={data.notes}
                        onChange={(e) => setData({ ...data, notes: e.target.value })}
                    />

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

function TuyaManualSection() {

    const { data, setData, loading, status, save } = useConfigSection("tuya_manual_devices", { items: [] });

    if (loading) return null;

    function updateItem(i, field, value) {
        const items = [...data.items];
        items[i] = { ...items[i], [field]: value };
        setData({ ...data, items });
    }

    function removeItem(i) {
        setData({ ...data, items: data.items.filter((_, idx) => idx !== i) });
    }

    function addItem() {
        setData({ ...data, items: [...data.items, { name: "", type: "", notes: "" }] });
    }

    return (
        <Card sx={{ p: 2, mb: 3 }}>
            <CardContent>
                <SectionLabel color="secondary">
                    Dispositivos Adicionados Manualmente
                </SectionLabel>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Catálogo simples pra manter registro do que existe na casa — sem controle automático ainda.
                </Typography>

                <Stack spacing={2}>
                    {data.items.map((item, i) => (
                        <Box key={i} sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                            <TextField
                                label="Nome"
                                value={item.name}
                                onChange={(e) => updateItem(i, "name", e.target.value)}
                                sx={{ flex: "1 1 160px" }}
                            />
                            <TextField
                                label="Tipo"
                                value={item.type}
                                onChange={(e) => updateItem(i, "type", e.target.value)}
                                sx={{ flex: "1 1 160px" }}
                            />
                            <TextField
                                label="Observações"
                                value={item.notes}
                                onChange={(e) => updateItem(i, "notes", e.target.value)}
                                sx={{ flex: "2 1 220px" }}
                            />
                            <IconButton onClick={() => removeItem(i)}>
                                <DeleteIcon />
                            </IconButton>
                        </Box>
                    ))}

                    <Button startIcon={<AddIcon />} onClick={addItem} sx={{ alignSelf: "flex-start" }}>
                        Adicionar dispositivo
                    </Button>

                    {status && <Alert severity={status.type}>{status.text}</Alert>}

                    <Button variant="contained" onClick={() => save(data)} sx={{ alignSelf: "flex-start" }}>
                        Salvar
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    );
}

export default function Settings() {

    return (
        <Box>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
                Configurações
            </Typography>

            <FredSection />
            <RemindersSection />
            <FloorPlanSection />
            <GoogleCalendarSection />
            <NabuCasaSection />
            <TuyaManualSection />
            <HomeAssistantSection />
            <MikrotikSection />
            <NetworkDevicesSection />
        </Box>
    );
}
