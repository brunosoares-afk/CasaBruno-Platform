import { Box, Typography } from "@mui/material";

// Cabeçalho de seção com mais peso visual que um texto cinza solto: barra
// de cor + linha em degradê preenchendo o resto da largura. Cor por
// categoria (mesma paleta já usada nos SwitchCard) pra ajudar a escanear
// a tela mais rápido.
export default function SectionLabel({ children, color = "primary", sx }) {

    return (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5, ...sx }}>

            <Box sx={{ width: 4, height: 14, borderRadius: 1, bgcolor: `${color}.main`, flexShrink: 0 }} />

            <Typography sx={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", whiteSpace: "nowrap" }}>
                {children}
            </Typography>

            <Box
                sx={(theme) => ({
                    flex: 1,
                    height: "1px",
                    background: `linear-gradient(90deg, ${theme.palette[color].main}55, transparent)`,
                })}
            />

        </Box>
    );
}
