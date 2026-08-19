import { useEffect, useRef, useState } from "react";
import {
    Alert,
    Box,
    Button,
    IconButton,
    MenuItem,
    Stack,
    TextField,
    Tooltip,
    Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

import api from "../../services/api";
import SectionLabel from "../../components/dashboard/SectionLabel";
import { useHomeAssistantStates } from "../../hooks/useHomeAssistantStates";
import { useFloorPlanMarkers, useSaveFloorPlanMarkers } from "../../hooks/useFloorPlanMarkers";
import { MARKER_ICONS } from "../homeassistant/views/inicio/FloorPlanPanel";

const MARKER_DOMAINS = ["light", "switch", "scene", "cover", "media_player", "person"];

const EMPTY_FORM = { entity_id: "", label: "", icon: "Lightbulb", type: "state", hide_when_inactive: false };

function newMarkerId() {
    return `m${Date.now()}${Math.floor(Math.random() * 1000)}`;
}

export default function FloorPlanMarkersEditor({ floorPlanUrl }) {

    const { data: states } = useHomeAssistantStates();
    const { data: savedMarkers } = useFloorPlanMarkers();
    const saveMarkers = useSaveFloorPlanMarkers();

    const [markers, setMarkers] = useState([]);
    const [loadedOnce, setLoadedOnce] = useState(false);
    const [form, setForm] = useState(EMPTY_FORM);
    const [placing, setPlacing] = useState(false);
    const [status, setStatus] = useState(null);

    const containerRef = useRef(null);
    const draggingId = useRef(null);

    // Só inicializa o estado local a partir do servidor uma vez — depois
    // disso o usuário edita localmente até clicar em Salvar.
    useEffect(() => {
        if (!loadedOnce && savedMarkers) {
            setMarkers(savedMarkers);
            setLoadedOnce(true);
        }
    }, [savedMarkers, loadedOnce]);

    const entityOptions = (states || []).filter((s) => MARKER_DOMAINS.includes(s.entity_id.split(".")[0]));

    function positionFromEvent(e) {
        const rect = containerRef.current.getBoundingClientRect();
        const x_pct = Math.min(100, Math.max(0, ((e.clientX - rect.left) / rect.width) * 100));
        const y_pct = Math.min(100, Math.max(0, ((e.clientY - rect.top) / rect.height) * 100));
        return { x_pct, y_pct };
    }

    function handleContainerClick(e) {
        if (!placing || !form.entity_id) return;
        const { x_pct, y_pct } = positionFromEvent(e);
        // person.* não liga/desliga — o estado real é "home"/"not_home",
        // não "on"/"off" como os outros domínios suportados aqui.
        const activeStates = form.entity_id.startsWith("person.") ? ["home"] : ["on"];
        setMarkers((prev) => [...prev, { id: newMarkerId(), ...form, x_pct, y_pct, active_states, anim_style: form.type === "state" ? "glow" : "bounce" }]);
        setPlacing(false);
        setForm(EMPTY_FORM);
    }

    function handlePointerDown(id) {
        draggingId.current = id;
    }

    function handlePointerMove(e) {
        if (!draggingId.current) return;
        const { x_pct, y_pct } = positionFromEvent(e);
        setMarkers((prev) => prev.map((m) => (m.id === draggingId.current ? { ...m, x_pct, y_pct } : m)));
    }

    function handlePointerUp() {
        draggingId.current = null;
    }

    function removeMarker(id) {
        setMarkers((prev) => prev.filter((m) => m.id !== id));
    }

    async function handleSave() {
        setStatus(null);
        try {
            await saveMarkers.mutateAsync(markers);
            setStatus({ type: "success", text: "Marcadores salvos." });
        } catch {
            setStatus({ type: "error", text: "Não foi possível salvar os marcadores." });
        }
    }

    return (
        <Box sx={{ mt: 3 }}>
            <SectionLabel color="success">
                Marcadores (ícones que reagem ao estado real)
            </SectionLabel>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Escolha uma entidade e um ícone, clique em "Adicionar" e depois clique no ponto da
                imagem onde ele deve aparecer. Marcadores já colocados podem ser arrastados.
            </Typography>

            <Box
                ref={containerRef}
                onClick={handleContainerClick}
                onPointerMove={handlePointerMove}
                onPointerUp={handlePointerUp}
                onPointerLeave={handlePointerUp}
                sx={{
                    position: "relative",
                    maxWidth: 480,
                    aspectRatio: "4 / 3",
                    mb: 2,
                    borderRadius: 1,
                    overflow: "hidden",
                    cursor: placing ? "crosshair" : "default",
                    border: "1px solid rgba(255,255,255,.15)",
                }}
            >
                <Box
                    component="img"
                    src={floorPlanUrl}
                    alt="Planta da casa"
                    draggable={false}
                    sx={{ width: "100%", height: "100%", objectFit: "contain", display: "block", userSelect: "none" }}
                />

                {markers.map((m) => {
                    const Icon = MARKER_ICONS[m.icon] || MARKER_ICONS.Lightbulb;
                    return (
                        <Tooltip key={m.id} title={m.label || m.entity_id}>
                            <Box
                                onPointerDown={(e) => { e.stopPropagation(); handlePointerDown(m.id); }}
                                onClick={(e) => e.stopPropagation()}
                                sx={{
                                    position: "absolute",
                                    left: `${m.x_pct}%`,
                                    top: `${m.y_pct}%`,
                                    transform: "translate(-50%, -50%)",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 0.5,
                                    cursor: "grab",
                                    bgcolor: "rgba(0,0,0,.5)",
                                    borderRadius: 1,
                                    p: 0.25,
                                }}
                            >
                                <Icon fontSize="small" />
                                <IconButton size="small" onClick={() => removeMarker(m.id)} sx={{ p: 0.25 }}>
                                    <DeleteIcon sx={{ fontSize: 14 }} />
                                </IconButton>
                            </Box>
                        </Tooltip>
                    );
                })}
            </Box>

            <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
                <TextField
                    select
                    label="Entidade"
                    size="small"
                    value={form.entity_id}
                    onChange={(e) => {
                        const entity = entityOptions.find((s) => s.entity_id === e.target.value);
                        setForm({ ...form, entity_id: e.target.value, label: entity?.attributes?.friendly_name || e.target.value });
                    }}
                    sx={{ minWidth: 220 }}
                >
                    {entityOptions.map((s) => (
                        <MenuItem key={s.entity_id} value={s.entity_id}>
                            {s.attributes?.friendly_name || s.entity_id}
                        </MenuItem>
                    ))}
                </TextField>

                <TextField
                    select
                    label="Ícone"
                    size="small"
                    value={form.icon}
                    onChange={(e) => setForm({ ...form, icon: e.target.value })}
                    sx={{ minWidth: 140 }}
                >
                    {Object.keys(MARKER_ICONS).map((name) => (
                        <MenuItem key={name} value={name}>{name}</MenuItem>
                    ))}
                </TextField>

                <TextField
                    select
                    label="Tipo"
                    size="small"
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                    sx={{ minWidth: 140 }}
                >
                    <MenuItem value="state">Fica aceso (luz, tomada)</MenuItem>
                    <MenuItem value="pulse">Pisca uma vez (portão, cena)</MenuItem>
                </TextField>

                <TextField
                    select
                    label="Quando inativo"
                    size="small"
                    value={form.hide_when_inactive ? "hide" : "dim"}
                    onChange={(e) => setForm({ ...form, hide_when_inactive: e.target.value === "hide" })}
                    sx={{ minWidth: 160 }}
                    disabled={form.type !== "state"}
                >
                    <MenuItem value="dim">Fica apagado</MenuItem>
                    <MenuItem value="hide">Some da planta</MenuItem>
                </TextField>

                <Button
                    variant={placing ? "contained" : "outlined"}
                    disabled={!form.entity_id}
                    onClick={() => setPlacing(true)}
                >
                    {placing ? "Clique na imagem..." : "Adicionar"}
                </Button>
            </Stack>

            {status && <Alert severity={status.type} sx={{ mb: 2 }}>{status.text}</Alert>}

            <Button variant="contained" onClick={handleSave} disabled={saveMarkers.isPending}>
                Salvar marcadores
            </Button>
        </Box>
    );
}
