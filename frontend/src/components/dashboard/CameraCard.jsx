import { useEffect, useState } from "react";
import { Card, Box, Typography, Dialog, IconButton } from "@mui/material";
import { keyframes } from "@emotion/react";
import VideocamOffIcon from "@mui/icons-material/VideocamOff";
import CloseIcon from "@mui/icons-material/Close";
import { cameraSnapshotUrl } from "../../api/homeassistantService";

const pulse = keyframes`
    0%, 100% { opacity: 1; }
    50% { opacity: .35; }
`;

export default function CameraCard({ entityId, name, refreshMs = 15000 }) {

    const [src, setSrc] = useState(() => cameraSnapshotUrl(entityId));
    const [failed, setFailed] = useState(false);
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {

        const interval = setInterval(() => {
            setSrc(cameraSnapshotUrl(entityId));
        }, refreshMs);

        return () => clearInterval(interval);

    }, [entityId, refreshMs]);

    return (

        <Card
            sx={(theme) => ({
                mb: 1.5,
                overflow: "hidden",
                border: "1px solid",
                borderColor: failed ? "error.main" : "rgba(255,255,255,.08)",
                boxShadow: failed
                    ? `0 0 16px -6px ${theme.palette.error.main}`
                    : `0 0 16px -6px ${theme.palette.success.main}`,
                transition: "border-color .2s ease, box-shadow .2s ease",
            })}
        >

            <Box sx={{ px: 1.5, pt: 1.2, display: "flex", alignItems: "center", gap: 1 }}>

                <Box
                    sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        flexShrink: 0,
                        bgcolor: failed ? "error.main" : "success.main",
                        animation: failed ? "none" : `${pulse} 2s ease-in-out infinite`,
                    }}
                />

                <Typography sx={{ fontSize: 12, fontWeight: 600, whiteSpace: "normal", wordBreak: "break-word", flex: 1 }}>
                    {name}
                </Typography>

            </Box>

            <Box
                sx={{ position: "relative", aspectRatio: "16 / 9", bgcolor: "background.default", mt: 1, cursor: failed ? "default" : "pointer" }}
                onClick={() => !failed && setExpanded(true)}
            >

                {/* <img> fica sempre montado, mesmo depois de falhar — é o
                onLoad dele que detecta a recuperação (próximo snapshot do
                intervalo). Escondendo em vez de desmontar, senão onError/
                onLoad nunca mais disparam e "indisponível" fica permanente
                mesmo com a câmera voltando a responder. */}
                <Box
                    component="img"
                    src={src}
                    onError={() => setFailed(true)}
                    onLoad={() => setFailed(false)}
                    sx={{ width: "100%", height: "100%", objectFit: "cover", display: failed ? "none" : "block" }}
                />

                {failed && (
                    <Box sx={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 0.5 }}>
                        <VideocamOffIcon sx={{ color: "error.main", fontSize: 28 }} />
                        <Typography sx={{ fontSize: 12, color: "error.main", fontWeight: 600 }}>
                            Câmera indisponível
                        </Typography>
                    </Box>
                )}

            </Box>

            <Dialog open={expanded} onClose={() => setExpanded(false)} maxWidth="lg" fullWidth>
                <Box sx={{ position: "relative", bgcolor: "background.default" }}>
                    <IconButton
                        onClick={() => setExpanded(false)}
                        sx={{ position: "absolute", top: 8, right: 8, bgcolor: "rgba(0,0,0,.5)", color: "#fff", "&:hover": { bgcolor: "rgba(0,0,0,.7)" } }}
                    >
                        <CloseIcon />
                    </IconButton>
                    <Box component="img" src={src} sx={{ width: "100%", display: "block" }} />
                </Box>
            </Dialog>

        </Card>

    );

}
