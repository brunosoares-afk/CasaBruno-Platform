import { useState } from "react";
import { Card, Box, Typography, IconButton, Popover } from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

function formatLastChanged(iso) {
    if (!iso) return null;
    const diffMs = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 1) return "agora mesmo";
    if (mins < 60) return `há ${mins} min`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `há ${hours}h`;
    return new Date(iso).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export default function SwitchCard({ icon, name, isOn, onToggle, stateLabel, color = "primary", lastChanged }) {

    const [anchorEl, setAnchorEl] = useState(null);

    return (

        <Card
            onClick={onToggle}
            sx={(theme) => ({
                p: 2,
                mb: 1.5,
                cursor: onToggle ? "pointer" : "default",
                display: "flex",
                alignItems: "center",
                gap: 2,
                border: "1px solid",
                borderColor: isOn ? `${color}.main` : "rgba(255,255,255,.08)",
                bgcolor: isOn ? `${theme.palette[color].main}22` : undefined,
                boxShadow: isOn ? `0 0 18px -4px ${theme.palette[color].main}` : "none",
                transition: "transform .15s ease, box-shadow .2s ease, border-color .2s ease",
                "&:hover": onToggle ? { transform: "translateY(-2px)" } : undefined,
                "&:active": onToggle ? { transform: "scale(0.98)" } : undefined,
            })}
        >

            <Box
                sx={(theme) => ({
                    width: 42,
                    height: 42,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    bgcolor: isOn ? `${color}.main` : "rgba(255,255,255,.06)",
                    color: isOn ? "#fff" : "text.secondary",
                    boxShadow: isOn ? `0 0 14px -2px ${theme.palette[color].main}` : "none",
                    transition: "all .2s ease",
                    "& svg": { fontSize: 22 },
                })}
            >
                {icon}
            </Box>

            <Box sx={{ minWidth: 0, flex: 1 }}>
                <Typography sx={{ fontSize: 14, fontWeight: 600, whiteSpace: "normal", wordBreak: "break-word" }}>
                    {name}
                </Typography>
                <Typography sx={{ fontSize: 11, fontWeight: isOn ? 700 : 400, color: isOn ? `${color}.main` : "text.secondary" }}>
                    {stateLabel ?? (isOn ? "Ligado" : "Desligado")}
                </Typography>
            </Box>

            {lastChanged && (
                <>
                    <IconButton
                        size="small"
                        onClick={(e) => { e.stopPropagation(); setAnchorEl(e.currentTarget); }}
                        sx={{ color: "text.secondary", flexShrink: 0 }}
                    >
                        <InfoOutlinedIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <Popover
                        open={Boolean(anchorEl)}
                        anchorEl={anchorEl}
                        onClose={(e) => { e?.stopPropagation?.(); setAnchorEl(null); }}
                        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
                        transformOrigin={{ vertical: "top", horizontal: "right" }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <Box sx={{ p: 1.5, minWidth: 160 }}>
                            <Typography sx={{ fontSize: 11, color: "text.secondary" }}>
                                Última mudança
                            </Typography>
                            <Typography sx={{ fontSize: 13, fontWeight: 600 }}>
                                {formatLastChanged(lastChanged)}
                            </Typography>
                        </Box>
                    </Popover>
                </>
            )}

        </Card>

    );

}
