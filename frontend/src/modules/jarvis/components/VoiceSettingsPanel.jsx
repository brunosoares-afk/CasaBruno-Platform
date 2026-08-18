import { useState } from "react";
import {
    Box,
    Collapse,
    Button,
    MenuItem,
    Select,
    Typography,
} from "@mui/material";
import { speakText } from "../services/fredApi";

// Kokoro (cbos-kokoro) soa melhor mas é ~2.3x mais lento que tempo real
// nesta CPU — Piper (cbos-piper) continua disponível pra quem preferir
// resposta mais rápida. Ver voice_service.py.
const VOICES = [
    { value: "pm_alex", label: "Alex — Kokoro (padrão)" },
    { value: "pm_santa", label: "Santa — Kokoro" },
    { value: "pf_dora", label: "Dora — Kokoro" },
    { value: "pt_BR-cadu-medium", label: "Cadu — Piper (mais rápido)" },
    { value: "pt_BR-faber-medium", label: "Faber — Piper" },
    { value: "pt_BR-jeff-medium", label: "Jeff — Piper" },
    { value: "pt_BR-edresson-low", label: "Edresson — Piper" },
];

export default function VoiceSettingsPanel({ open, voice, onVoiceChange }) {

    const [testing, setTesting] = useState(false);

    async function handleTest() {
        setTesting(true);
        try {
            const blob = await speakText("Oi, eu sou o Fred.", voice);
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.onended = () => URL.revokeObjectURL(url);
            await audio.play();
        } finally {
            setTesting(false);
        }
    }

    return (
        <Collapse in={open}>
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    p: 2,
                    mt: 2,
                    borderRadius: 2,
                    border: "1px solid rgba(255,255,255,.08)",
                }}
            >
                <Typography variant="body2" color="text.secondary">
                    Voz do Fred
                </Typography>

                <Select
                    size="small"
                    value={voice}
                    onChange={(e) => onVoiceChange(e.target.value)}
                >
                    {VOICES.map((v) => (
                        <MenuItem key={v.value} value={v.value}>
                            {v.label}
                        </MenuItem>
                    ))}
                </Select>

                <Button
                    size="small"
                    variant="outlined"
                    onClick={handleTest}
                    disabled={testing}
                >
                    {testing ? "Testando..." : "Testar voz"}
                </Button>
            </Box>
        </Collapse>
    );
}
