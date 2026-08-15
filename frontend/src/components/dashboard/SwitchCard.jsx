import { Card, Box, Typography } from "@mui/material";

export default function SwitchCard({ icon, name, isOn, onToggle, stateLabel, color = "primary" }) {

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

        </Card>

    );

}
