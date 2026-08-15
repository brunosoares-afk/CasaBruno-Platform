import { Card, Box, Typography } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import WhatsAppIcon from "@mui/icons-material/WhatsApp";
import LanguageIcon from "@mui/icons-material/Language";
import SectionLabel from "./SectionLabel";

const CHANNEL_ICON = {
    voice: <MicIcon fontSize="inherit" />,
    whatsapp: <WhatsAppIcon fontSize="inherit" />,
    web: <LanguageIcon fontSize="inherit" />,
};

function timeAgo(iso) {
    const diffMs = Date.now() - new Date(iso).getTime();
    const minutes = Math.floor(diffMs / 60000);
    if (minutes < 1) return "agora";
    if (minutes < 60) return `${minutes} min atrás`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h atrás`;
    return `${Math.floor(hours / 24)}d atrás`;
}

export default function ActivityFeed({ items }) {

    return (

        <Box>

            <SectionLabel color="info">
                COMANDOS RECENTES
            </SectionLabel>

            <Card sx={{ p: 1.5 }}>

                {(!items || items.length === 0) && (
                    <Typography sx={{ fontSize: 12, color: "text.secondary", p: 1 }}>
                        Nenhum comando ainda.
                    </Typography>
                )}

                {items?.map((item, i) => (

                    <Box
                        key={i}
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1.5,
                            py: 1,
                            borderTop: i > 0 ? "1px solid rgba(255,255,255,.06)" : "none",
                        }}
                    >

                        <Box sx={{ color: item.success ? "primary.main" : "error.main", display: "flex", fontSize: 18 }}>
                            {CHANNEL_ICON[item.channel] || <LanguageIcon fontSize="inherit" />}
                        </Box>

                        <Typography sx={{ fontSize: 13, flex: 1, minWidth: 0, whiteSpace: "normal", wordBreak: "break-word" }}>
                            {item.text}
                        </Typography>

                        <Typography sx={{ fontSize: 10, color: "text.secondary", flexShrink: 0, whiteSpace: "normal" }}>
                            {timeAgo(item.created_at)}
                        </Typography>

                    </Box>

                ))}

            </Card>

        </Box>

    );

}
