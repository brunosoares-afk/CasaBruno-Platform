import { Box } from "@mui/material";

// Reaproveita o app "Casa" (controle financeiro, /opt/casa) como está —
// backend/frontend próprios, sem reescrever nada aqui. Só embutimos a PWA
// dele numa aba do painel do Fred (pedido do Bruno 2026-09-13: unificar os
// dois projetos numa única tela). Servido publicamente via NPM em /financas
// (proxy_pass com barra final, pra descartar o prefixo antes de chegar no
// servidor Node do Casa — sem isso ele recebe "/financas/api/..." e não
// reconhece a rota); o próprio Casa detecta esse prefixo e ajusta
// CONFIG.API_URL sozinho (ver publico/index.html). Login próprio (não
// depende mais de um token fixo — ver [[casa-token-leak-fixed-2026-09-13]]),
// então expor isso publicamente é seguro.
const CASA_URL = "https://hda08fx9s7v.sn.mynetname.net/financas/";

export default function FinancasView() {
  return (
    <Box sx={{ height: "calc(100vh - 220px)" }}>
      <Box
        component="iframe"
        src={CASA_URL}
        title="Casa - Controle Financeiro"
        sx={{
          height: "100%",
          width: "100%",
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 2,
        }}
      />
    </Box>
  );
}
