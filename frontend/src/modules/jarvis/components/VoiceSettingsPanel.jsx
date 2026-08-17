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

// Vozes Piper pt-BR locais (container cbos-piper) — trocado da Azure/HA
// Cloud em 2026-08-16 para tirar a dependência do HA (ver memória
// casa-bruno-voice-piper-migration-2026-08-16).
const VOICES = [
    { value: "pt_BR-faber-medium", label: "Faber (padrão)" },
    { value: "pt_BR-jeff-medium", label: "Jeff" },
    { value: "pt_BR-cadu-medium", label: "Cadu" },
    { value: "pt_BR-edresson-low", label: "Edresson" },
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
