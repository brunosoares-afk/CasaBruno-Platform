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

// Vozes neurais pt-BR da Azure via HA Cloud (Nabu Casa) — trocado do
// Piper local, que soava robótico demais (ver memória
// casa-bruno-custom-frontend-dashboard).
const VOICES = [
    { value: "AntonioNeural", label: "Antônio (padrão)" },
    { value: "DonatoNeural", label: "Donato" },
    { value: "FranciscaNeural", label: "Francisca" },
    { value: "BrendaNeural", label: "Brenda" },
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
