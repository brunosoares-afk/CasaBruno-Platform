import { Box, Card, Typography } from "@mui/material";

import { useJarvis } from "../../modules/jarvis/context/JarvisContext";
import { getFredStatus } from "../../modules/jarvis/utils/fredStatus";
import FredOrb from "./FredOrb";

const STATE_SUBTITLE = {
    inactive: "Só chamar quando precisar.",
    listening: "De olho, esperando o comando.",
    capturing: "Ouvindo...",
    thinking: "Pensando na resposta...",
    speaking: "Falando...",
    error: "Alguma coisa travou no microfone.",
};

// Card de destaque do personagem — mesmo FredOrb do header, só que
// grande, com nome e legenda do estado atual. Fica logo no topo do
// Início pra dar "presença" ao Fred em vez dele só existir como ícone
// pequeno no cabeçalho.
export default function FredCharacterCard() {
    const { supported, micEnabled, listenStatus, processing, micError } = useJarvis();
    const status = getFredStatus({ supported, micEnabled, listenStatus, processing, micError });

    return (
        <Card
            sx={{
                display: "flex",
                alignItems: "center",
                gap: 2.5,
                p: 2.5,
                background: "linear-gradient(135deg, rgba(255,255,255,.03) 0%, rgba(255,255,255,0) 100%)",
            }}
        >
            <FredOrb state={status.state} size={96} />

            <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                    Fred
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    {STATE_SUBTITLE[status.state] || status.label}
                </Typography>
            </Box>
        </Card>
    );
}
